# Generated by Django 4.2.19 on 2025-02-22 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
