from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# Create your views here.

import logging
from django.views.generic import View
from django.http import Http404, HttpResponse
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.template.base import Template, Context
from django.utils.encoding import smart_text
from django.conf import settings
from django.db.models import Q
from .models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


class USSD(View):

    def get(self, request, *args, **kwargs):
        logger.error('Data:API:get - currently inactive: %s', str(request))
        raise Http404()

    def post(self, request, *args, **kwargs):
        logger.debug('Received USSD Post')

        session = None
        page_content = u"END Unspecified Error"
        try:

            ussd_params = {}
            ussd_params['phone_number'] = request.POST.get('phoneNumber')
            ussd_params['session_id'] = request.POST.get('sessionId')
            ussd_params['service_code'] = request.POST.get('serviceCode')
            ussd_params['user_input'] = request.POST.get('text')
            ussd_params['network_code'] = request.POST.get('networkCode')
            logger.debug('Got USSD Post Info')
            page_content = self.process(ussd_params)
        except Exception as e:
            logger.exception("Failed to read USSD Post. {}".format(e))
            if settings.DEBUG:
                page_content = u"END USSD Error: %s" % str(e)
            else:
                page_content = u"END USSD session has ended"
        logger.debug(u"Sending %s" % page_content)
        response = HttpResponse(page_content, content_type='text/plain')
        return response

    def process(self, ussd_params):
        page_content = u"END Unspecified Error"

        if ussd_params['phone_number'] and ussd_params['session_id']:
            logger.debug("Phone number %s" % ussd_params['phone_number'])
            logger.debug("Session ID %s" % ussd_params['session_id'])
            session = self.get_session(ussd_params)
            # if not session.account:
            #     session.set_account()
            logger.debug(u"Got session %s" % str(session))
            this_page = self.get_next_page(session)
            if this_page:
                session.last_page = this_page
                session.save()
                page_content = self.render_page(session, this_page)
                print('page_cont',page_content)
            else:
                logger.debug("Have no page to render")
                page_content = u"END USSD session has ended"
                return page_content
        else:
            page_content = u"END We did not receive the details of you mobile device"

        return page_content

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # api_key = ApiKey.authenticate(request, username=settings.USSD_USER_NAME)
        # if not api_key:
        #     logger.error('Attempted call to API only view: {}.'.format(self.__class__.__name__))
        #     raise Http404()
        return View.dispatch(self, request, *args, **kwargs)

    def get_session(self, ussd_params):
        session = None
        try:
            session = USSDSession.objects.get(session_id=ussd_params['session_id'])
            logger.debug(u"Existing session")
        except USSDSession.DoesNotExist:
            session = USSDSession()
            session.session_id = ussd_params['session_id']
            logger.debug(u"Created new session")
        session.user_response = ussd_params['user_input']
        session.phone_number = ussd_params['phone_number']
        session.service_code = ussd_params['service_code']
        session.carrier = self.get_carrier(ussd_params['network_code'])
        session.save()
        return session

    def get_carrier(self, networkcode):

        #Use case 1:- if the network code exists then return the carrier
        #Use case 2: if the network code doesn't exist extract the country and use it to get the default carrier
        #Use case 3:- Return any carrier if no carrier is specified as default
        carrier = None
        try:
            carrier = USSDCarrier.objects.get(code=networkcode)

        except USSDCarrier.DoesNotExist:
            import mobile_codes
            mcc = networkcode[0:3]
            try:
                country_iso = mobile_codes.mcc(mcc)[0].alpha2 #tested for Uganda,Zambia,Nigeria
            except Exception as e:
                logging.exception(e.message)
            else:
                try:
                    carrier = USSDCarrier.objects.get(country__iso_2_abbreviation=country_iso,country_default=True)
                except USSDCarrier.DoesNotExist:
                    try:
                        carrier = USSDCarrier.objects.filter(country__iso_2_abbreviation=country_iso)[0]
                    except IndexError:
                        pass
        return carrier



    def get_next_page(self, session):
        logger.debug("Session carrier %s" % session.carrier)
        next_page = None
        print('se',session.last_user_input)
        logger.debug(u"Getting default page move")
        if session.last_user_input:
            try:
                last_user_input = session.last_user_input
                print('last_user_input', last_user_input)
                if session.last_page:
                    print('Got it')
                    try:
                        logger.debug(
                            u'Getting next page move: last_page:{} - last_input {}'.format(session.last_page,
                                                                                           last_user_input))
                        page_move = USSDPageMove.objects.get(page=session.last_page,
                                                             required_user_input=last_user_input)
                    except USSDPageMove.DoesNotExist as e:
                        try:
                            logger.debug(u"Getting next wildcard page move")
                            page_move = USSDPageMove.objects.filter(Q(page=session.last_page),
                                                                    Q(required_user_input=None) | Q(
                                                                        required_user_input=''))[0]
                            print('current', page_move)
                        except IndexError:
                            logger.debug(u"Invalid Page Move: %s" % str(last_user_input))
                            # Go back to previous page for unrecognised inputs
                            next_page = session.last_page
                            print('next_page', next_page)

            except ValueError:
                logger.debug(u"Invalid User Input")
                if session.last_page:
                    # Go back to previous page for non int inputs
                    next_page = session.last_page


        else:
            print('Nothing')
            if session.last_page:
                page_move = USSDPageMove.objects.filter(next_page=session.last_page,next_page__carrier=session.carrier).first()
                print('page_move',page_move.page,page_move.next_page)
            else:
                page_move = USSDPageMove.objects.filter(page=session.last_page,next_page__carrier=session.carrier).first()
        if not next_page and session.carrier is not None and page_move is not None:
            if self.validate_page_move(session,page_move):
                    next_page = page_move.next_page
            else:
                next_page = page_move.error_page
        return next_page

    def validate_page_move(self, session, page_move):
        print('validate page move')
        if page_move.validation_code:
            logger.debug(u"Got validation code %s" % page_move.validation_code)
            if page_move.validation_code.startswith("validation_"):
                try:
                    validation_function = getattr(session, page_move.validation_code)
                    if validation_function():
                        logger.debug(u"Validated successfully %s" % page_move.validation_code)
                    else:
                        logger.debug(u"Validation failed %s" % page_move.validation_code)
                        return False
                except AttributeError as e:
                    logger.exception("Validation code in USSDPageMove %d does not exist:%s" % (page_move.id, str(e)))
                    return False
            else:
                logger.error("Invalid validation function: %s" % page_move.validation_code)
                return False
        if page_move.page_tasks:
            print('page_tasks',page_move,page_move.page_tasks)
            logger.debug(u"Got page_tasks code %s" % page_move.page_tasks)
            if page_move and page_move.page_tasks.startswith("page_task_"):
                try:
                    page_task_function = getattr(session, page_move.page_tasks)
                    print('page_task',page_task_function)
                    if page_task_function:
                        print('task completed successfully')
                        session.page_task_id = page_task_function
                        session.save()
                        logger.debug(u"Task completed successfully: %s" % page_move.page_tasks)
                    else:
                        logger.debug(u"Task failed: %s" % page_move.page_tasks)
                        return False
                except AttributeError as e:
                    print('error',str(e))
                    logger.exception("page task code in USSDPageMove %d does not exist:%s" % (page_move.id, str(e)))
                    return False
            else:
                logger.error("Invalid page_task function: %s" % page_move.page_tasks)
                return False
        return True

    def render_page(self, session, page):
        print('render_page',page)
        page_content = u"END Unspecified Error"
        content_template_string = None
        content_template_string = USSDPageContent.objects.get(page=page).content
        print('content_te',content_template_string)
        if content_template_string:
            logger.debug("Got template string")
            try:
                content_template = Template(content_template_string)
                page_content = content_template.render(Context({"session": session}))
                if page.page_moves.all():
                    page_content = "CON %s" % page_content
                else:
                    page_content = "END %s" % page_content
            except Exception as e:
                logger.exception("Template Rendering (%s) Error: %s" % (str(page), str(e)))
                if settings.DEBUG:
                    page_content = u"END USSD Template Error: %s" % str(e)
        return page_content
