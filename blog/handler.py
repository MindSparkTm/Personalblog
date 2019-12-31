from django.conf import settings
from celery import shared_task
import logging
logger = logging.getLogger(__name__)
from .models import UserProfile
from django.contrib.auth.models import User

@shared_task
def create_user_profile(user_id,**kwargs):
    try:
        data = u'{}{}'.format(user_id,kwargs['subscribed'])
        logging.debug(u"Got User Profile Creation %s" % data)
        subscribed = kwargs['subscribed']
        user = User.objects.get(id=user_id)
        UserProfile.objects.get_or_create(user=user,subscribed=subscribed)

    except Exception as e:
        logging.exception(str(e))
