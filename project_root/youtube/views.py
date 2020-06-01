from django.shortcuts import render
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from .forms import LoginForm, RegisterForm, NewVideoForm, CommentForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Video, Comment
import string, random
from django.core.files.storage import FileSystemStorage
import os
from wsgiref.util import FileWrapper

class VideoFileView(View):
    
    def get(self, request, file_name):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = FileWrapper(open(BASE_DIR+'/'+file_name, 'rb'))
        response = HttpResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        return response


class HomeView(View):
    template_name = 'index.html'
    def get(self, request):
        most_recent_videos = Video.objects.order_by('-datetime')[:8]
        return render(request, self.template_name, {'menu_active_item': 'home', 'most_recent_videos': most_recent_videos})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')

class VideoView(View):
    template_name = 'video.html'

    def get(self, request, id):
        #fetch video from DB by ID
        video_by_id = Video.objects.get(id=id)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_by_id.path = 'http://localhost:8000/get_video/'+video_by_id.path
        context = {'video':video_by_id}
        
        if request.user.is_authenticated:
            print('user signed in')
            comment_form = CommentForm()
            context['form'] = comment_form

        
        comments = Comment.objects.filter(video__id=id).order_by('-datetime')[:5]
        print(comments)
        context['comments'] = comments
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
            return HttpResponseRedirect('/video/{}'.format(str(video_id)))
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
        
        form = NewVideoForm()
        return render(request, self.template_name, {'form':form})

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

            fs = FileSystemStorage(location = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filename = fs.save(path, file)
            file_url = fs.url(filename)

            print(fs)
            print(filename)
            print(file_url)

            new_video = Video(title=title, 
                            description=description,
                            user=request.user,
                            path=path)
            new_video.save()
            
            # redirect to detail view template of a Video
            return HttpResponseRedirect('/video/{}'.format(new_video.id))
        else:
            return HttpResponse('Your form is not valid. Go back and try again.')

