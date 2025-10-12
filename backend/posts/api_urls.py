from rest_framework.routers import DefaultRouter
from .views import PostViewSet, TagViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = router.urls
