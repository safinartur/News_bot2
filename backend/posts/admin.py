from django.contrib import admin
from .models import Post, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "published")
    list_filter = ("published", "tags")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
