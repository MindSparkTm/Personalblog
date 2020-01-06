from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.views.generic import CreateView,DetailView,DeleteView,UpdateView,View,ListView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile,Post,PostCategory
from .forms import PostForm,UserForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login
from django.urls import reverse
from django.contrib import messages
import logging
# Create your views here.

logger = logging.getLogger(__name__)

def home(request):
    if request.method=='GET':
        return redirect('blog:post_category_list',category='project')
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

    def get_context_data(self, **kwargs):
        context = super(CreatePost, self).get_context_data(**kwargs)
        context['post_nav'] = 'active'
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        messages.success(self.request, "Your post has been successfully created")
        return super(CreatePost,self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',kwargs={'pk': self.object.pk})

class PostDetailView(DetailView):
    model = Post
    template_name= "blog/post_detail.html"

class PostDeleteView(DeleteView):
    model = Post

    def get_success_url(self):
        post_category = Post.objects.get(id=self.object.pk)
        category = post_category.category.lower()
        return reverse('blog:post_category_list',kwargs={'category': category})


class PostUpdateView(UpdateView):
    model = Post
    fields = ['title','description','image']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('blog:post_detail',kwargs={'pk': self.object.pk})


class PostListView(ListView):
    model = Post
    fields = ['title','description','image']
    template_name ='blog/post_list.html'

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        logger.info('Category: %s', str(self.kwargs['category']))
        if self.kwargs['category']=='home':
            self.kwargs['category']='Django'
        category = PostCategory.objects.get(name=self.kwargs['category'])
        logger.info('Post category: %s %s', str(category),str(self.kwargs['category']))
        context['post_nav'] = 'active'
        context['category_desc'] = category.description
        logger.info('Post category description: %s', str(category.description))
        return context

    def get_queryset(self):
        if self.kwargs['category']=='home':
            self.kwargs['category']='project'
        return Post.objects.select_related('category_name').filter(category=self.kwargs['category'])


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
                    return redirect('blog:post_category_list',category='project')
                else:
                    return render(request,'blog/login.html',{'msg':'Invalid credentials'})
            else:
                return render(request, 'blog/login.html', {'msg': 'Please enter valid credentials'})
        except Exception as e:
            print('Exception',e)

def RegisterView(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            return redirect('blog:post_category_list',category='project')
    else:
        form = UserForm()
    return render(request, 'blog/login.html', {'form': form})

def AboutMe(request):
    if request.method =='GET':
        try:
            post = Post.objects.filter(category='ABOUT ME')[0]
        except Post.DoesNotExist:
            post = None
        except IndexError:
            return redirect('blog:create_post')

        else:
            return render(request,'blog/about _me.html',{'post':post,'post_about_me':'active'})


