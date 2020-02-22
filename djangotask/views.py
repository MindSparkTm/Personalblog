from django.shortcuts import render, HttpResponse
from .tools import get_content_type, get_browser_detail \
    , get_client_ip, get_query_string
from .models import ClientRequestDetail
from .serializers import ClientRequestDetailSerializer
from rest_framework.generics import ListAPIView
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_request_details(request):
    query_string = get_query_string(request)
    if query_string:
        client_ip = get_client_ip(request)
        browser_detail = get_browser_detail(request)
        content_type = get_content_type(request)
        request_data = 'Request data IP- {ip},' \
                       'BrowserDetail- {browser_detail},' \
                       'ContentType - {content_type},' \
                       'QueryString - {query_string}'
        logging.info(request_data
                     .format(ip=client_ip,
                             browser_detail=browser_detail,
                             content_type=content_type,
                             query_string=query_string))

        client_request_details, _ = ClientRequestDetail. \
            objects.get_or_create(ip=client_ip,
                                  browser_detail=browser_detail,
                                  content_type=content_type,
                                  query_string=query_string)
        return HttpResponse('success')
    else:
        return HttpResponse('Query string *param1* missing in request')


class ClientRequestDetailApiView(ListAPIView):
    serializer_class = ClientRequestDetailSerializer
    queryset = ClientRequestDetail.objects.all()
