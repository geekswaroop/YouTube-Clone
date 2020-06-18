from django.shortcuts import render
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from .forms import LoginForm, RegisterForm, NewVideoForm, CommentForm, ChannelForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Video, Comment, Channel, Like, Dislike, Video_View, Channel_Subscription
import string, random
from django.core.files.storage import FileSystemStorage
import os
from wsgiref.util import FileWrapper
from django.utils import timezone

class ChannelView(View):
    template_name = "channelview.html"

    def get(self, request, user):
        videos = Video.objects.filter(user__username = user).order_by("-datetime")
        context = {'videos': videos}
        context['channel'] = Channel.objects.filter(user__username = user).get()

        if request.user.is_authenticated:
            channel = Channel.objects.get(user__username = user)
            if Channel_Subscription.objects.filter(user=request.user, channel=channel).count() == 0:
                context['subscribed'] = False
            else:
                context['subscribed'] = True
        
        return render(request, self.template_name, context)


class CreateChannelView(View):
    template_name = "channel.html"

    def get(self, request):
        if request.user.is_authenticated:
            try:
                if Channel.objects.filter(user__username = request.user).get().channel_name != "":
                    return HttpResponseRedirect('/')
            except Channel.DoesNotExist:
                form = ChannelForm()
                channel = False
                return render(request, self.template_name, {'form': form, 'channel': channel})
    
    
    def post(self, request):
        # pass filled out HTML-Form from View to RegisterForm()
        form = ChannelForm(request.POST)
        if form.is_valid():
            # create a User account
            print(form.cleaned_data['channel_name'])
            channel_name = form.cleaned_data['channel_name']
            user = request.user
            subscribers = 0
            new_channel = Channel(channel_name=channel_name, user=user, subscribers=subscribers)
            new_channel.save()
            return HttpResponseRedirect('/')
        return HttpResponse('This is Register view. POST Request.')

        
class VideoFileView(View):
    
    def get(self, request, file_name):
        # print("YYY")
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("HELLO")
        print(BASE_DIR)
        print(file_name)
        file = FileWrapper(open(BASE_DIR+'/youtube/static/videos/'+file_name, 'rb'))
        response = HttpResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        return response


class HomeView(View):
    template_name = 'index.html'
    def get(self, request):
        most_recent_videos = Video.objects.order_by('-datetime')[:8]
        most_recent_channels = Channel.objects.filter()
        
        channel = False
        print(request.user.username)
        if request.user.username != "":
            # print("YEs")
            try:
                channel = Channel.objects.filter(user__username = request.user)
                print(channel)
                channel = channel.get()
            except Channel.DoesNotExist:
                channel = False
            # if channel: 
        # print(request.user)
        return render(request, self.template_name, {'menu_active_item': 'home', 'most_recent_videos': most_recent_videos, 'most_recent_channels': most_recent_channels, 'channel': channel})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class VideoView(View):
    template_name = 'video.html'

    def get(self, request, id, new):
        
        # Increment number of views
        if new == 1:
            video_by_id = Video.objects.get(id=id)
            n = video_by_id.number_of_views
            video_by_id.number_of_views = n+1
            video_by_id.save()

        video_by_id = Video.objects.get(id=id)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_by_id.path = 'http://localhost:8000/get_video/'+video_by_id.path
        print(video_by_id)
        print(video_by_id.path)

        context = {'video':video_by_id}
        
        if request.user.is_authenticated:
            print('user signed in')
            comment_form = CommentForm()
            context['form'] = comment_form
        
        comments = Comment.objects.filter(video__id=id).order_by('-datetime')
        print(comments)
        context['comments'] = comments

        if request.user.is_authenticated:
            if Like.objects.filter(video=video_by_id, user = request.user).count() == 0:
                context['likes'] = True
            else:
                context['likes'] = False
        
            if Dislike.objects.filter(video=video_by_id, user = request.user).count() == 0:
                context['dislikes'] = True
            else:
                context['dislikes'] = False

            if Video_View.objects.filter(video=video_by_id, user = request.user).count() == 0:
                new_view = Video_View(video = video_by_id, user = request.user, datetime = timezone.now())
                new_view.save()
            else:
                view = Video_View.objects.get(video=video_by_id, user = request.user)
                view.datetime = timezone.now()
                view.save()

        context['likes_count'] = Like.objects.filter(video = video_by_id).count()
        context['dislikes_count'] = Dislike.objects.filter(video = video_by_id).count()

        try:
            channel = Channel.objects.filter(user__username = request.user).get().channel_name != ""
            print(channel)
            context['channel'] = channel
        except Channel.DoesNotExist:
            channel = False

        uploader = video_by_id.user
        uploader_channel = Channel.objects.get(user = uploader)
        context['uploader_channel'] = uploader_channel

        return render(request, self.template_name, context)


class LoginView(View):
    template_name = 'login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            #logout(request)
            return HttpResponseRedirect('/')

        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # pass filled out HTML-Form from View to LoginForm()
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # create a new entry in table 'logs'
                login(request, user)
                print('success login')
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('login')
        return HttpResponse('This is Login view. POST Request.')

class CommentView(View):
    template_name = 'comment.html'

    def post(self, request):
        # pass filled out HTML-Form from View to CommentForm()
        form = CommentForm(request.POST)
        if form.is_valid():
            # create a Comment DB Entry
            text = form.cleaned_data['text']
            video_id = request.POST['video']
            video = Video.objects.get(id=video_id)
            
            new_comment = Comment(text=text, user=request.user, video=video)
            new_comment.save()
            return HttpResponseRedirect('/video/{}/{}/'.format(str(video_id), str(0)))
        return HttpResponse('This is Register view. POST Request.')

class RegisterView(View):
    template_name = 'register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            print('already logged in. Redirecting.')
            print(request.user)
            return HttpResponseRedirect('/')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # pass filled out HTML-Form from View to RegisterForm()
        form = RegisterForm(request.POST)
        if form.is_valid():
            # create a User account
            print(form.cleaned_data['username'])
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            new_user.save()
            return HttpResponseRedirect('/login')
        return HttpResponse('This is Register view. POST Request.')

class NewVideo(View):
    template_name = 'new_video.html'

    def get(self, request):
        if request.user.is_authenticated == False:
            #return HttpResponse('You have to be logged in, in order to upload a video.')
            return HttpResponseRedirect('/register')
        
        try:
            channel = Channel.objects.filter(user__username = request.user).get().channel_name != "" 
            if channel:
                # print("HHHEEEEE     ", Channel.objects.filter(user__username = request.user).get().channel_name)
                form = NewVideoForm() 
                return render(request, self.template_name, {'form':form, 'channel':channel})
        except Channel.DoesNotExist:
            return HttpResponseRedirect('/')

    def post(self, request):
        # pass filled out HTML-Form from View to NewVideoForm()
        form = NewVideoForm(request.POST, request.FILES)       

        if form.is_valid():
            # create a new Video Entry
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            file = form.cleaned_data['file']

            random_char = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            path = random_char+file.name
            print("TTTTTTT     ",path)
            fs = FileSystemStorage(location = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filename = fs.save("youtube/static/videos/"+path, file)
            file_url = fs.url(filename)

            print(fs)
            print(filename)
            print(file_url)

            new_video = Video(title=title, 
                            description=description,
                            user=request.user,
                            path=path,
                            number_of_views = 0,
                            datetime = timezone.now())
            new_video.save()
            
            # redirect to detail view template of a Video
            return HttpResponseRedirect('/video/{}/{}/'.format(new_video.id, str(1)))
        else:
            return HttpResponse('Your form is not valid. Go back and try again.')


def video_like(request, v_id, u_id):
    video = Video.objects.get(id=v_id)
    user = User.objects.get(id=u_id)
    new_like = Like(user = user, video = video)
    new_like.save()
    return HttpResponseRedirect('/video/{}/{}/'.format(str(v_id), str(0)))

def video_unlike(request, v_id, u_id):
    video = Video.objects.get(id=v_id)
    user = User.objects.get(id=u_id)
    like = Like.objects.get(user=user, video=video)
    like.delete()
    return HttpResponseRedirect('/video/{}/{}/'.format(str(v_id), str(0)))

def video_dislike(request, v_id, u_id):
    video = Video.objects.get(id=v_id)
    user = User.objects.get(id=u_id)
    new_dislike = Dislike(user = user, video = video)
    new_dislike.save()
    return HttpResponseRedirect('/video/{}/{}/'.format(str(v_id), str(0)))

def video_undislike(request, v_id, u_id):
    video = Video.objects.get(id=v_id)
    user = User.objects.get(id=u_id)
    dislike = Dislike.objects.get(user=user, video=video)
    dislike.delete()
    return HttpResponseRedirect('/video/{}/{}/'.format(str(v_id), str(0)))


def liked_videos(request):
    context = {}
    if request.user.is_authenticated:
        likes = Like.objects.filter(user = request.user)
        context['likes'] = likes

    try:
        channel = Channel.objects.filter(user__username = request.user).get().channel_name != ""
        print(channel)
        context['channel'] = channel
    except Channel.DoesNotExist:
        channel = False
        
    return render(request, "liked_videos.html", context)

def watch_history(request):
    context = {}
    if request.user.is_authenticated:
        views = Video_View.objects.filter(user = request.user).order_by('-datetime')
        context['views'] = views

    try:
        channel = Channel.objects.filter(user__username = request.user).get().channel_name != ""
        print(channel)
        context['channel'] = channel
    except Channel.DoesNotExist:
        channel = False

    return render(request, "watch_history.html", context)

def trending(request):
    context = {}
    videos = Video.objects.all().order_by('-number_of_views')[:5]
    context['videos'] = videos

    try:
        channel = Channel.objects.filter(user__username = request.user).get().channel_name != ""
        print(channel)
        context['channel'] = channel
    except Channel.DoesNotExist:
        channel = False

    return render(request, "trending.html", context)

def help(request):
    return render(request, "aboutUs.html", {})

def channel_subscribe(request, c_id):
    user = request.user
    channel = Channel.objects.get(id = c_id)
    new_subscription = Channel_Subscription(user = user, channel = channel)
    new_subscription.save()

    n = channel.subscribers 
    channel.subscribers = n+1
    channel.save()

    return HttpResponseRedirect('/{}/channel'.format(channel.user.username))

def channel_unsubscribe(request, c_id):
    user = request.user
    channel = Channel.objects.get(id = c_id)
    subscription = Channel_Subscription.objects.get(user = user, channel = channel)
    subscription.delete()

    n = channel.subscribers 
    channel.subscribers = n-1
    channel.save()

    return HttpResponseRedirect('/{}/channel'.format(channel.user.username))

def subscriptions(request):
    context = {}

    if request.user.is_authenticated:
        videos = []
        user_subscriptions = Channel_Subscription.objects.filter(user = request.user)
        for subscription in user_subscriptions:
            channel = subscription.channel
            owner = channel.user
            videos.extend(list(Video.objects.filter(user = owner)))
        
        context['videos'] = videos

    try:
        channel = Channel.objects.filter(user__username = request.user).get().channel_name != ""
        print(channel)
        context['channel'] = channel
    except Channel.DoesNotExist:
        channel = False

    return render(request, "subscriptions.html", context)

def channels_list(request):
    context = {}
    channels = Channel.objects.all()
    context['channels'] = channels

    try:
        channel = Channel.objects.filter(user__username = request.user).get().channel_name != ""
        print(channel)
        context['channel'] = channel
    except Channel.DoesNotExist:
        channel = False

    return render(request, 'channels_list.html', context)