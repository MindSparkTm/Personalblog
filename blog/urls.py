from django.conf.urls import url
from .views import Home,subscribe_user,CreatePost,\
    PostDetailView,PostDeleteView,PostUpdateView,LoginView,RegisterView,AboutMe,\
    DjangoPost,PythonPost,OtherPost,PythonPostDetail,DjangoPostDetail,OtherPostDetail
app_name ='blog'
urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='blog_login'),
    url(r'^register/$', RegisterView, name='blog_register'),
    url(r'^about-me/$', AboutMe, name='blog_about_me'),
    url(r'^django/$', DjangoPost, name='blog_django'),
    url(r'^python/$', PythonPost, name='blog_python'),
    url(r'^python/(?P<python_pk>\w+)/$', PythonPostDetail, name='python_post_detail'),
    url(r'^django/(?P<django_pk>\w+)/$', DjangoPostDetail, name='django_post_detail'),
    url(r'^other/$', OtherPost, name='blog_other'),
    url(r'^other/(?P<other_pk>\w+)/$', OtherPostDetail, name='blog_other_detail'),
    url(r'^home/$', Home.as_view(), name='home'),
    url(r'^subscribe/$', subscribe_user, name='subscribed_user'),
    url(r'^post/create/$', CreatePost.as_view(), name='create_post'),
    url(r'^post/(?P<pk>\w+)/$',PostDetailView.as_view(),name='post_detail'),
    url(r'^post/(?P<pk>\w+)/delete/$', PostDeleteView.as_view(), name='post_delete'),
    url(r'^post/(?P<pk>\w+)/update/$', PostUpdateView.as_view(), name='post_update'),

]