from django.contrib import admin
from .models import Video, Comment, Channel, Like, Dislike, Video_View, Channel_Subscription
# Register your models here.

admin.site.register([Video, Comment, Channel, Like, Dislike, Video_View, Channel_Subscription])