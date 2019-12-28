from django.conf.urls import url
from .views import USSD
app_name ='ussd'
urlpatterns = [
    url(r'^ussd/', USSD.as_view(), name='ussd'),
]