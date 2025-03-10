# Generated by Django 5.1.6 on 2025-03-01 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
