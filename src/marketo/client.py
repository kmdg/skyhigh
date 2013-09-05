__author__ = 'michael'

import os
import sys
import logging
import traceback
import datetime
import hmac
import binascii
import hashlib
from time import sleep, time
from urllib2 import URLError

from django.conf import settings


if __name__ == "__main__":
    if not os.path.exists('src'):
        sys.exit('Please run this script from the root of the project source tree')

    # fix the path
    sys.path[0:0] = ['src']

from suds.client import Client, WebFault


# exception classes
class SoapClientValidationError(Exception):  pass
class SoapClientServiceError(Exception):  pass
class SoapClientError(Exception):  pass


# grab a reference to the marketo log handler - see settings.py for details
logger = logging.getLogger('marketo.suds.client')


class SoapClient(object):
    """
    A suds client for Marketo web services
    """
    def _get_service_client(self):
        client = None
        retries = settings.MARKETO_SOAP_CLIENT_RETRIES
        while retries > 0:
            try:
                retries -= 1
                client = Client(settings.MARKETO_SOAP_SERVICE_URL, timeout=settings.MARKETO_SOAP_CLIENT_CONNECTION_TIMEOUT)
                break
            except (WebFault, URLError):
                if retries <= 0:
                    # raise with the last error message
                    raise SoapClientError('Request failed with: %s' % sys.exc_info()[1])

                logger.warning('Connection error (will be retried %d more '\
                               'times in the next %d seconds: %s' % (retries,
                                                                     settings.MARKETO_SOAP_CLIENT_RETRY_SLEEP, sys.exc_info()[1]))
                sleep(settings.MARKETO_SOAP_CLIENT_RETRY_SLEEP)
            except:
                logger.exception('Service failed: %s' % traceback.format_exc())
                raise

        logger.debug('Service client: %s' % client)
        return client


    @staticmethod
    def get_service_obj(client, klass, **kwargs):
        so = client.factory.create(klass)
        for k, v in kwargs.iteritems():
            setattr(so, k, v)
        return so


    @staticmethod
    def get_client_service_name(client):
        return len(client.sd) and client.sd[0].service.name or 'undefined'


    def _get_service_response(self, client, method, *args):
        start_time = time()
        logger.debug('Service call: %s' % method)
        response = None

        auth_header = client.factory.create('AuthenticationHeaderInfo')
        auth_header.mktowsUserId = settings.MARKETO_SOAP_SERVICE_API_UID
        auth_header.requestTimestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        auth_header.requestSignature = binascii.hexlify(hmac.new(settings.MARKETO_SOAP_SERVICE_API_KEY,
            msg='%s%s' % (auth_header.requestTimestamp, auth_header.mktowsUserId),
            digestmod=hashlib.sha1).digest())
        client.set_options(soapheaders=auth_header)

        # change the end-point - the wsdl's points to localhost
        client.set_options(location=settings.MARKETO_SOAP_SERVICE_ENDPOINT)

        retries = settings.MARKETO_SOAP_CLIENT_RETRIES
        while retries > 0:
            try:
                retries -= 1
                response = getattr(client.service, method)(*args)
                break
            except (URLError,):
                if retries <= 0:
                    # raise with the last error message
                    raise SoapClientError('Request for service %s failed with: %s' % (
                        self.get_client_service_name(client), sys.exc_info()[1]))

                logger.warning('Connection error (will be retried %d more '\
                               'times in the next %d seconds: %s' % (retries,
                                                                     settings.MARKETO_SOAP_CLIENT_RETRY_SLEEP, sys.exc_info()[1]))
                sleep(settings.MARKETO_SOAP_CLIENT_RETRY_SLEEP)
            except:
                logger.exception('Service [%s] failed: %s' % (
                    self.get_client_service_name(client), traceback.format_exc()))
                raise

        logger.info('Response time: [%9.3f]s for [%s]' % (time() - start_time, self.get_client_service_name(client)))
        return response


    def get_lead(self, lead_id=None, email=None):
        client = self._get_service_client()
        lead_key = self.get_service_obj(client, 'LeadKey')
        if lead_id:
            lead_key.keyType = 'IDNUM'
            lead_key.keyValue = lead_id
        elif email:
            lead_key.keyType = 'EMAIL'
            lead_key.keyValue = email
        else:
            raise SoapClientValidationError('No key has been specified')

        try:
            response = self._get_service_response(client, 'getLead', *(lead_key,))
        except WebFault:
            # lead does not exist
            response = None

        return response


    def sync_lead(self, lead_id=None, email=None, username=None, lead_attrs=[], marketo_cookie=None):
        client = self._get_service_client()
        lead_rec = self.get_service_obj(client, 'LeadRecord')
        lead_rec.Id = lead_id
        lead_rec.Email = email
        lead_rec.ForeignSysPersonId = username

        lead_rec.leadAttributeList.attribute = [
        self.get_service_obj(client, 'Attribute', attrName=lead_attr[0], attrValue=lead_attr[1])
        for lead_attr in lead_attrs]

        args = (lead_rec,)

        if marketo_cookie:
            args += (0, marketo_cookie)

        response = self._get_service_response(client, 'syncLead', *args)
        return response

def sync_lead_by_email(email, attrs, marketo_cookie=None):
    """
    Syncs a lead from the Marketo database by email
    """
    return SoapClient().sync_lead(
        email=email,
        lead_attrs=((key, attrs[key]) for key in attrs.keys()),
        marketo_cookie=marketo_cookie,
    )

def get_lead_by_email(email):
    """
    Gets a lead from the Marketo database by email
    """
    return SoapClient().get_lead(email=email)



if __name__ == "__main__":
    my_client = SoapClient()

    #    # add lead the first time, or nth time - username is unique id at Marketo
    #    response = my_client.sync_lead(email='max@unomena.com', username='max.naude')
    #    print response
    #
    #    # remember the lead id
    #    lead_id = response.leadId
    #    print 'Lead ID: %s' % lead_id
    #
    #    # find previous lead by id returned in response:
    #    response = my_client.get_lead(lead_id=lead_id)
    #    print response
    #
    #    # mod the lead score
    #    response = my_client.sync_lead(lead_id=lead_id, lead_attrs=(('LeadScore', 5),))
    #    print response
    #
    #    # check update successful
    #    response = my_client.get_lead(lead_id=lead_id)
    #    print response
    #
    #    # mod the lead score
    #    response = my_client.sync_lead(lead_id=lead_id, lead_attrs=(('LeadScore', 2),))
    #    print response

    # check response successful
    response = my_client.get_lead(email='maxnaude@gmail.com')
    print response

    # check response unsuccessful
    response = my_client.get_lead(email='not.a.user@unomena.com')
    print response
