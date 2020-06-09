from django.contrib import admin
from django.urls import path
from youtube.views import HomeView, NewVideo, CommentView, LoginView, RegisterView, VideoView, VideoFileView, LogoutView, CreateChannelView, ChannelView
from youtube import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view()),
    path('login', LoginView.as_view()),
    path('register', RegisterView.as_view()),
    path('new_video', NewVideo.as_view()),
    path('video/<int:id>', VideoView.as_view()),
    path('comment', CommentView.as_view()),
    path('get_video/<file_name>', VideoFileView.as_view()),
    path('logout', LogoutView.as_view()),
    path('createchannel', CreateChannelView.as_view()),
    path('<user>/channel', ChannelView.as_view()),
    # path('video_like/<int:v_id>/<int:u_id>', LikeView.as_view()),
    path('video/<int:v_id>/<int:u_id>/like', views.video_like, name='video_like'),
    path('video/<int:v_id>/<int:u_id>/unlike', views.video_unlike, name='video_unlike')
]

from django.conf import settings
from django.conf.urls import include, url  # For django versions before 2.0
from django.urls import include, path  # For django versions from 2.0 and up

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns