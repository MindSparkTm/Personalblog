from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .manager import UserManager
from tinymce.models import HTMLField
import logging
from django.conf import settings

# Create your models here.
logger = logging.getLogger(__name__)

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
        logger.info('Send email initiated 1: %s', str(self.user.email))
        self._send_email()

    def _send_email(self):
        try:
            logger.info('Send email initiated 2: %s', str(self.user.email))
            subject = "You have been added to Rj's mailing list"
            message = "Hey Welcome to Rj's blog. You have been subscribed and you will receive some " \
                  "amazing notifications when something awesome is published"
            send_mail(subject, message, 'smartsurajit2008@gmail.com',
                   [self.user.email])
        except Exception as e:
            logger.exception('Sending Email exception',str(e))

class PostCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    url = models.CharField(max_length=50,blank=True,null=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'PostCategory'
        verbose_name_plural = 'PostCategories'

    def __str__(self):
        return u'{}'.format(self.name)

    def set_url(self):
        return u'{}{}{}'.format('/',self.name.lower(),'/')

    def save(self, *args, **kwargs):
        self.url = self.set_url()
        super(PostCategory, self).save(*args, **kwargs)

class PostSubCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    category = models.ForeignKey(PostCategory,on_delete=models.CASCADE)
    url = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        verbose_name = 'PostSubCategory'
        verbose_name_plural = 'PostSubCategories'

    def __str__(self):
        return u'{}{}'.format(self.name,self.description)

    def set_url(self):
        return u'{}/{}/'.format(self.category.name,self.name)

    def save(self, *args, **kwargs):
        self.url = self.set_url()
        super(PostSubCategory, self).save(*args, **kwargs)

class Post(models.Model):
    category = [
        ('project', 'PROJECT'),
        ('about me', 'ABOUT ME'),
        ('Python', 'PYTHON'),
        ('Django', 'DJANGO'),
        ('Other','Other'),
        ]
    title = models.CharField(max_length=100)
    description = HTMLField()
    image = models.ImageField(upload_to='images/',blank=True,null=True,default='images/1024px-No_image_available.svg.png')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='post',null=True)
    category = models.CharField(max_length=20,choices=category,default='project')
    category_name = models.ForeignKey(PostCategory,on_delete=models.CASCADE,related_name='post',null=True)
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



