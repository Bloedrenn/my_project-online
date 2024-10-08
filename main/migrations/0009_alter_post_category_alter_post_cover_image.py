# Generated by Django 5.1.1 on 2024-10-07 19:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_post_cover_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='main.category'),
        ),
        migrations.AlterField(
            model_name='post',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
