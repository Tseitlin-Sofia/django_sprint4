from django.contrib import admin

from .models import Category, Comment, Location, Post, PublishedModel

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Location)
admin.site.register(Post)
