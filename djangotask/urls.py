from django.conf.urls import url
from .views import get_request_details,ClientRequestDetailApiView
app_name='djangotask'
urlpatterns = [
  url(r'^request/$', get_request_details, name='request'),
  url(r'^request-detail/$', ClientRequestDetailApiView.as_view(),
      name='request-api'),
]