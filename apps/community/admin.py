from django.contrib import admin

from apps.community.models.post_model import Post


class CommunityAdmin(admin.ModelAdmin):
    class Media:
        model = Post
