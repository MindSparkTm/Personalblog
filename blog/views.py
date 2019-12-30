from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.views.generic import CreateView,DetailView,DeleteView,UpdateView,View,ListView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile,Post
from .forms import PostForm,UserForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login
# Create your views here.

class Home(ListView):
    template_name = 'blog/home.html'
    model = Post
    fields = '__all__'
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(category='PROJECT')

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
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

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super(CreatePost,self).form_valid(form)

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
            login(request, user)
            return redirect('blog:home')
    else:
        form = UserForm()
    return render(request, 'blog/login.html', {'form': form})

def AboutMe(request):
    if request.method =='GET':
        try:
            post = Post.objects.filter(category='ABOUT ME',user=request.user)[0]
        except Post.DoesNotExist:
            post = None
        except IndexError:
            return redirect('blog:create_post')

        else:
            return render(request,'blog/about _me.html',{'post':post,'post_about_me':'active'})


class DjangoPost(ListView):
    template_name = 'blog/django.html'
    model = Post
    fields = '__all__'
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(category='DJANGO')

    def get_context_data(self, **kwargs):
        context = super(DjangoPost, self).get_context_data(**kwargs)
        context['post_django'] = 'active'
        return context

class PythonPost(ListView):
    template_name = 'blog/python.html'
    model = Post
    fields = '__all__'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(category='PYTHON')

    def get_context_data(self, **kwargs):
        context = super(PythonPost, self).get_context_data(**kwargs)
        context['post_python'] = 'active'
        return context

def PythonPostDetail(request,python_pk):
    if request.method =='GET':
        try:
            post = Post.objects.filter(category='PYTHON',id=python_pk)[0]
        except Post.DoesNotExist:
            post = None
        except IndexError:
            return redirect('blog:home')

        else:
            return render(request,'blog/python_post_detail.html',{'post':post,'post_python':'active'})

def DjangoPostDetail(request,django_pk):
    if request.method =='GET':
        try:
            post = Post.objects.filter(category='DJANGO',id=django_pk)[0]
        except Post.DoesNotExist:
            post = None
        except IndexError:
            return redirect('blog:home')

        else:
            return render(request,'blog/django_post_detail.html',{'post':post,'post_django':'active'})

def OtherPostDetail(request,other_pk):
    if request.method =='GET':
        try:
            post = Post.objects.filter(category='OTHER',id=other_pk)[0]
        except Post.DoesNotExist:
            post = None
        except IndexError:
            return redirect('blog:home')

        else:
            return render(request,'blog/other_post_detail.html',{'post':post,'other_django':'active'})
class OtherPost(ListView):
    template_name = 'blog/other.html'
    model = Post
    fields = '__all__'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(category='OTHER')

    def get_context_data(self, **kwargs):
        context = super(OtherPost, self).get_context_data(**kwargs)
        context['post_other'] = 'active'
        return context