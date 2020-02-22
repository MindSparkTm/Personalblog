import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    except Exception as ex:
        logger.exception('Tool:Exception in getting client ip %s', str(ex))
        return
    else:
        return ip


def get_browser_detail(request):
    try:
        browser_type = request.META['HTTP_USER_AGENT']
    except Exception as ex:
        logger.exception('Tool:Exception in getting browser detail %s', str(ex))
        return
    else:
        return browser_type


def get_content_type(request):
    try:
        content_type = request.META.get('HTTP_ACCEPT')
    except Exception as ex:
        logger.exception('Tool:Exception in getting content type %s', str(ex))
        return
    else:
        return content_type


def get_query_string(request):
    query_param = request.GET.get('param1', None)
    return query_param
