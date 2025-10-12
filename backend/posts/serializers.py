import os
from rest_framework import serializers
from .models import Post, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]

class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_slugs = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "body", "created_at", "published", "cover", "tags", "tag_slugs", "source_url"]

    def create(self, validated_data):
        tag_slugs = validated_data.pop("tag_slugs", [])
        post = Post.objects.create(**validated_data)
        if tag_slugs:
            tags = []
            from .models import Tag
            for slug in tag_slugs:
                tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": slug.replace("-", " ").title()})
                tags.append(tag)
            post.tags.set(tags)
        return post


    def validate(self, attrs):
        cover = self.initial_data.get('cover')
        if cover and hasattr(cover, 'size'):
            max_size = int(os.getenv('MAX_UPLOAD_SIZE', 5*1024*1024))
            if cover.size > max_size:
                raise serializers.ValidationError({'cover': 'Файл слишком большой. Максимум %s байт' % max_size})
        return attrs
