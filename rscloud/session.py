#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

import json
import os
import requests
from datetime import datetime
from dateutil.parser import parse as dt_parse

from .exceptions import RackspaceAuthError, RackspaceAPIError

AUTH_URL = 'https://identity.api.rackspacecloud.com/v2.0/'

class AuthenticatedSession(object):
    def __init__(self):
        """
        An authenticated session for the rackspace api.
        """
        self.username = None
        self.password = None
        self.api_key = None
        self.region = None
        self.auth_url = None

        self.sc = {}  # service catalog
        self.session = requests.session()
        self.session.headers = {'Content-Type': 'application/json',
                                'Accept': 'application/json'}
        # rackspace api has lots of connection errors
        # retry 3 times
        self.session.config['max_retries'] = 3

    def login(self, username, api_key=None, password=None,
              region=None, auth_url=None):
        """
        Authenticate the current session with the rackspace auth servers, and
        and retrieve the service catalog.


        """

        if username:
            self.username = username

        if api_key:
            self.api_key = api_key

        if password:
            self.password = password

        if region:
            self.region = region

        if auth_url:
            self.auth_url = auth_url
        elif not self.auth_url:
            self.auth_url = AUTH_URL

        if self.password:
            auth_data = {"auth":
                            {"passwordCredentials":
                                {"username": self.username,
                                 "password": self.password}
                            }
                        }
        elif self.api_key:
            auth_data = {"auth":
                            {"RAX-KSKEY:apiKeyCredentials":
                                {"username": self.username,
                                 "apiKey": self.api_key}
                            }
            }
        else:
            raise RackspaceAuthError('No password or api_key defined')

        resp = self.session.post(self.auth_url+'/tokens',
                                 data=json.dumps(auth_data))
        if resp.status_code != 200:
            raise RackspaceAuthError(resp.status_code, resp.content)

        self.auth_token = resp.json['access']['token']
        self.auth_user = resp.json['access']['user']

        if not self.region:
            self.region = self.auth_user['RAX-AUTH:defaultRegion']
        if not self.region:
            raise RackspaceAPIError('No default region found')

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
                if not self.region:
                    # don't know what region to pick, take the first
                    self.sc[service].update(ep)
                elif 'region' in ep and self.region == ep['region']:
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
