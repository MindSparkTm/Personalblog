from django.conf.urls import url
from .views import home,subscribe_user,CreatePost,\
    PostDetailView,PostDeleteView,PostUpdateView,LoginView,RegisterView,AboutMe,PostListView
app_name ='blog'
urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='blog_login'),
    url(r'^register/$', RegisterView, name='blog_register'),
    url(r'^about-me/$', AboutMe, name='blog_about_me'),
    url(r'^$', home, name='blog_home'),
    url(r'^(?P<category>\w+)/$', PostListView.as_view(), name='post_category_list'),
    url(r'^user/subscribe/$', subscribe_user, name='subscribed_user'),
    url(r'^post/create/$', CreatePost.as_view(), name='create_post'),
    url(r'^post/(?P<pk>\w+)/$',PostDetailView.as_view(),name='post_detail'),
    url(r'^post/(?P<pk>\w+)/delete/$', PostDeleteView.as_view(), name='post_delete'),
    url(r'^post/(?P<pk>\w+)/update/$', PostUpdateView.as_view(), name='post_update'),

]