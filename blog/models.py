from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from embed_video.fields import EmbedVideoField

class Tag(models.Model):
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.tag

class Post(models.Model):
    title = models.CharField(max_length=100)
    abstract = RichTextUploadingField(blank=True,config_name='special')
    image = models.ImageField(default='default.png',blank=True, upload_to='PostPics')
    post_tag = models.ManyToManyField(Tag,max_length=100)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    video  =  EmbedVideoField(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

class PostImage(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    sub_content = RichTextUploadingField(blank=True,config_name='special')
    images = models.FileField(blank=True,upload_to = 'images/')

    def __str__(self):
        return self.post.title

