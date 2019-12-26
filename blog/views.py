from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.views.generic import CreateView,DetailView,DeleteView,UpdateView,View
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404,redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile,Post
from .forms import PostForm,UserForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login
# Create your views here.

class Home(CreateView):
    template_name = 'blog/home.html'
    model = Post
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['post_list'] = Post.objects.all()
        context['home_nav'] = 'active'
        return context

def subscribe_user(request):
    if request.method == 'POST':
        email = request.POST.get("email",None)
        msg = 'You have been subscribed'
        if email is not None:
            try:
                user= User.objects.select_related('profile').get(email=email)
                if getattr(user,'profile'):
                    subscribed = user.profile.subscribed
                    if subscribed is False:
                        user.profile.subscribed = True
                        user.profile.save()
                    else:
                        msg = 'You are already subscribed'
            except User.DoesNotExist:
                UserProfile.objects.create_user_profile(email,subscribed=True,user_exist=False)
            except ObjectDoesNotExist:
                UserProfile.objects.create_user_profile(email,subscribed=True,user_exist=True)
        return JsonResponse({'msg':msg})


class CreatePost(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post.html'
    success_url = reverse_lazy('blog:home')

    def get_context_data(self, **kwargs):
        context = super(CreatePost, self).get_context_data(**kwargs)
        context['post_nav'] = 'active'
        return context
class PostDetailView(DetailView):
    model = Post

class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')


class PostUpdateView(UpdateView):
    model = Post
    fields = ['title','description','image']
    template_name_suffix = '_update_form'

class LoginView(View):

    def get(self,request):
        form = UserForm
        return render(request,'blog/login.html',{'form':form})
    def post(self,request):
        try:
            username = request.POST.get('username',None)
            password = request.POST.get('password',None)
            if username and password:
                user = authenticate(username=username,password=password)
                if user is not None:
                    login(request,user)
                    return redirect('blog:home')
                else:
                    return render(request,'blog/login.html',{'msg':'Invalid credentials'})
            else:
                return render(request, 'blog/login.html', {'msg': 'Please enter valid credentials'})
        except Exception as e:
            pass

def RegisterView(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user=form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            login(request, user)
            return redirect('blog:home')
    else:
        form = UserForm()
    return render(request, 'blog/login.html', {'form': form})

