from celery import shared_task
import logging
from accounts.models import UserProfile
logger = logging.getLogger(__name__)

@shared_task
def get_username(phone_number):
    print('phone_number',phone_number)
    user_profile = UserProfile.objects.get(phone_number=phone_number)
    print('profile', user_profile.user.username)
    return user_profile.user.username
