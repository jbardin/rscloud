#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

import json
import os
import requests
from datetime import datetime
from dateutil.parser import parse as dt_parse

from .exceptions import RackspaceAuthError, RackspaceAPIError

#AUTH_URL = 'https://identity.api.rackspacecloud.com/v2.0/tokens'


class AuthenticatedSession(object):
    def __init__(self, username=None, api_key=None, region=None, auth_url=None):
        """
        An authenticated session for the rackspace api.
        """

        self.sc = {}  # service catalog
        self.username = username
        self.api_key = api_key
        self.region = region
        self.auth_token = None
        self.expires = None
        self.auth_url = auth_url
        self.session = requests.session()
        self.session.headers = {'Content-Type': 'application/json',
                                'Accept': 'application/json'}
        # rackspace api has lots of connection errors
        # retry 3 times
        self.session.config['max_retries'] = 3

    def login(self, username=None, api_key=None, region=None, auth_url=None):
        """
        Credentials can be passed in directly, or are pulled from the os
        environment. The following environment variables are checked for
        the username/api_key pair:
        - $OS_USERNAME
        - $OS_PASSWORD
        - $OS_REGION_NAME
        """
        # look for username and api_key in some of the usual environment
        # variables before we bail out.
        if self.username:
            # noop: we're re-authenticating
            pass
        elif username:
            self.username = username
        else:
            if 'OS_USERNAME' in os.environ:
                self.username = os.environ['OS_USERNAME']
            else:
                raise RackspaceAuthError('username not defined')

        if self.api_key:
            pass
        elif api_key:
            self.api_key = api_key
        else:
            if 'OS_PASSWORD' in os.environ:
                self.api_key = os.environ['OS_PASSWORD']
            else:
                raise RackspaceAuthError('api_key not defined')

        if self.region:
            pass
        elif region:
            self.region = region
        else:
            if 'OS_REGION_NAME' in os.environ:
                self.region = os.environ['OS_REGION_NAME']
            else:
                raise RackspaceAuthError('region not defined')

        if self.auth_url:
            pass
        elif auth_url:
            self.auth_url = auth_url
        else:
            if 'OS_AUTH_URL' in os.environ:
                self.auth_url = os.environ['OS_AUTH_URL']
            else:
                raise RackspaceAuthError('auth_url not defined')

        auth_data = json.dumps({"auth": {"RAX-KSKEY:apiKeyCredentials":
                                        {"username": self.username,
                                         "apiKey": self.api_key}}
                                })

        resp = self.session.post(self.auth_url+'/tokens', data=auth_data)
        if resp.status_code != 200:
            raise RackspaceAuthError(resp.status_code, resp.content)

        self.auth_token = resp.json['access']['token']

        # parse the expires time into a utc time tuple, as dealing with tz
        # offsets is a pain.
        self.expires = dt_parse(self.auth_token['expires']).utctimetuple()

        self.session.headers['X-Auth-Token'] = self.auth_token['id']

        #from now on, raise all errors
        self.session.config['danger_mode'] = True

        service_catalog = resp.json['access']['serviceCatalog']

        # bind this to the session for debugging later
        self.service_catalog = service_catalog

        # flatten the endpoint for our region into the sc[service] dict,
        # keyed by service name
        for svc in service_catalog:
            service = svc['name']
            self.sc[service] = {}
            self.sc[service]['type'] = svc['type']
            for ep in svc['endpoints']:
                if 'region' in ep and self.region == ep['region']:
                    self.sc[service].update(ep)
                elif 'region' not in ep:
                    self.sc[service].update(ep)

    def _check_auth(self):
        # make sure we have an auth token, and it's not expired
        if not self.auth_token:
            raise RackspaceAuthError('Not logged in')
        if datetime.utcnow().timetuple() > self.expires:
            self.login()

    def check_callback(self, resp, details=False):
        resp = self.get(resp['callbackUrl'])
        print resp.json

    # delegate the http verbs to the request object
    # TODO: retry on various transient errors
    def get(self, url, **kwargs):
        self._check_auth()
        try:
            return self.session.get(url, **kwargs)
        except requests.HTTPError as err:
            raise RackspaceAPIError(err.response.text)

    def post(self, url, data=None, **kwargs):
        self._check_auth()
        try:
            return self.session.post(url, data=data, **kwargs)
        except requests.HTTPError as err:
            raise RackspaceAPIError(err.response.text)

    def put(self, url, data=None, **kwargs):
        self._check_auth()
        try:
            return self.session.put(url, data=data, **kwargs)
        except requests.HTTPError as err:
            raise RackspaceAPIError(err.response.text)

    def delete(self, url, **kwargs):
        self._check_auth()
        try:
            return self.session.delete(url, **kwargs)
        except requests.HTTPError as err:
            raise RackspaceAPIError(err.response.text)
