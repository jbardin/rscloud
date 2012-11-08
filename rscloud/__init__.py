#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

"""
Rackspace API access library
"""
import os

from .session import AuthenticatedSession
from .domains import Domains, Records
from .servers import Servers, Images, Flavors
from .servers_firstgen import FirstGenServers, FirstGenImages
from .exceptions import RackspaceAuthError, RackspaceAPIError


class RackspaceSession(object):
    def __init__(self, username=None, api_key=None, password=None,
                 region=None, auth_url=None):
        self.username = username
        self.api_key = api_key
        self.password = password
        self.region = region
        self.auth_url = auth_url
        self.rs_session = AuthenticatedSession()
        self.authenticated = False

    def login(self):
        """
        Login to the Rackspace cloud, and setup all our API endpoints

        """

        if not self.username:
            self.username = os.environ.get('OS_USERNAME')

        if not self.api_key:
            self.api_key = os.environ.get('OS_PASSWORD')

        if not self.region:
            self.region = os.environ.get('OS_REGION_NAME')

        # Authenticate with the Rackspace cloud
        self.rs_session.login(self.username, self.api_key, self.password,
                              self.region, self.auth_url)
        self.authenticated = True

        # collect our API endpoints
        self.servers = Servers(self.rs_session)
        self.servers.images = Images(self.rs_session)
        self.servers.flavors = Flavors(self.rs_session)
        self.servers_firstgen = FirstGenServers(self.rs_session)
        self.servers_firstgen.images = FirstGenImages(self.rs_session)
        self.domains = Domains(self.rs_session)
        self.domains.records = Records(self.rs_session)

        # alias the Session verbs here too
        self.get = self.rs_session.get
        self.put = self.rs_session.put
        self.post = self.rs_session.post
        self.delete = self.rs_session.delete

        return self
