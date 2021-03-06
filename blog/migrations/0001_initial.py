# Generated by Django 2.2.6 on 2020-07-26 05:14

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import embed_video.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('image', models.ImageField(blank=True, default='default.png', upload_to='PostPics')),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('video', embed_video.fields.EmbedVideoField(blank=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PostImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.FileField(upload_to='images/')),
                ('image_description', models.CharField(blank=True, max_length=100)),
                ('post', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='blog.Post')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='post_tag',
            field=models.ManyToManyField(max_length=100, to='blog.Tag'),
        ),
    ]
