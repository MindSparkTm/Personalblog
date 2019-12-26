from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.views.generic import CreateView,DetailView,DeleteView,UpdateView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404,redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile,Post
from .forms import PostForm
from django.urls import reverse_lazy

# Create your views here.

class Home(CreateView):
    template_name = 'blog/home.html'
    model = Post
    fields = '__all__'

    def get_context_data(self, **kwargs):
        print('entered this')
        context = super(Home, self).get_context_data(**kwargs)
        print('post',Post.objects.all())
        context['post_list'] = Post.objects.all()
        context['home_nav'] = 'active'
        return context

def subscribe_user(request):
    if request.method == 'POST':
        print('entered')
        email = request.POST.get("email",None)
        msg = 'You have been subscribed'
        if email is not None:
            try:
                user= User.objects.select_related('profile').get(email=email)
                if getattr(user,'profile'):
                    subscribed = user.profile.subscribed
                    print(subscribed)
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