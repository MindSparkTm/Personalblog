from django.db import models
from django.contrib.auth.models import User


class UserManager(models.Manager):

    def _create_user(self,email):
        password = User.objects.make_random_password()
        user = User.objects.create(email=email, username=email)
        user.set_password(password)
        user.save()
        return user

    def create_user_profile(self,email,**kwargs):
        if kwargs['user_exist'] is False:
            user = self._create_user(email)
        else:
            user = User.objects.get(email=email)
        user_profile = self.model(user=user,
        subscribed=kwargs['subscribed'])
        user_profile.save()
        user_profile.send_email()
        return user_profile