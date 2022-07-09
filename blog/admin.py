
from django.contrib import admin

from .models import Post, Subscribers, Comment, Video, Category,Reply 

admin.site.register(Video)
admin.site.register(Post)
admin.site.register(Subscribers)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Category)