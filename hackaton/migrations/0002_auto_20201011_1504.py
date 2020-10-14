# Generated by Django 2.2.6 on 2020-10-11 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackaton', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pyme',
            name='accuracy',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='cashResources',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='costSales',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='grossProfit',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='mnt_units',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='more_info',
            field=models.TextField(blank=True, default='here additional info', null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='netProfit',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='operatingProfit',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='profitBeforeTax',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='register_created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='sales',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='totalAssets',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='totalEquity',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='pyme',
            name='totalLiabilities',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
