# Generated by Django 2.2.6 on 2020-10-13 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackaton', '0003_auto_20201013_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pyme',
            name='pyme_document',
            field=models.FileField(blank=True, default='default.pdf', upload_to=''),
        ),
    ]
