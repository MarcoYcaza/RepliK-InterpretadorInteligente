from django.contrib import admin
from .models import Post ,PostImage ,Tag

class PostImageAdmin(admin.StackedInline):
    model = PostImage


class PostAdmin(admin.ModelAdmin):

    fields = ('title','abstract','post_tag','date_posted','author','video','image')

    inlines = [PostImageAdmin]

    class Meta:
       model = Post


class PostImageAdmin(admin.ModelAdmin):
    fields = ('images',)


class TagAdmin(admin.ModelAdmin):

    fields = ('tag',)

admin.site.register(Post,PostAdmin)
admin.site.register(Tag,TagAdmin)


