#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

"""
Rackspace API access library
"""

from .session import AuthenticatedSession
from .domains import Domains, Records
from .servers import Servers, Images, Flavors
from .servers_firstgen import FirstGenServers, FirstGenImages
from .exceptions import RackspaceAuthError, RackspaceAPIError


class RackspaceSession(object):
    def __init__(self, username=None, api_key=None, region=None,
                 auth_url=None):
        self.rs_session = AuthenticatedSession(username, api_key, region, auth_url)
        self.authenticated = False

    def login(self):
        """
        Login to the Rackspace cloud, and setup all our API endpoints
        """

        # Authenticate with the Rackspace cloud
        self.rs_session.login()

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
