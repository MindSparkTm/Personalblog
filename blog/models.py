from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .manager import UserManager
from celery import shared_task
from tinymce.models import HTMLField


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    subscribed = models.BooleanField(default = False)
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    class Meta:
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfiles'

    def __str__(self):
        return u'{}'.format(self.user.username)

    def send_email(self):
        self._send_email.delay(self.user.username,self.user.email)

    @shared_task
    def _send_email(username,email):
        subject = "You have been added to Rj's mailing list"
        message = "Hey Welcome to Rj's blog. You have been subscribed and you will receive some " \
                  "amazing notifications when something awesome is published"
        send_mail(subject, message, 'smartsurajit2008@gmail.com',
                   [email])

class Post(models.Model):
    category = [
        ('project', 'PROJECT'),
        ('about me', 'ABOUT ME'),
        ]
    title = models.CharField(max_length=100)
    description = HTMLField()
    image = models.ImageField(upload_to='images/',blank=True,null=True,default='images/blog-post-thumb-1.jpg')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='post',null=True)
    category = models.CharField(max_length=20,choices=category,default='project')
    date_last_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return u'{}'.format(self.title)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post_detail', args=[str(self.id)])
