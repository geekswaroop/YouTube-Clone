from django.contrib import admin
from .models import Video, Comment
# Register your models here.

admin.site.register([Video, Comment])