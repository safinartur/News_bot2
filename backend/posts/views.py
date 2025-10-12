from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import Post, Tag
from .serializers import PostSerializer, TagSerializer
from django.conf import settings

class IsBotOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Simple shared-key auth for automation and Telegram bot
        api_key = request.headers.get("X-API-KEY") or request.query_params.get("api_key")
        return api_key == getattr(settings, "API_SHARED_KEY", None)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related().prefetch_related("tags").all()
    serializer_class = PostSerializer
    permission_classes = [IsBotOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {"published": ["exact"], "tags__slug": ["exact"]}
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset().filter(published=True)
        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs

class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
