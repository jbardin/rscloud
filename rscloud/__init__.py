#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

"""
Rackspace API access library
"""

from .session import AuthenticatedSession
from .domains import Domains, Records
from .servers import Servers, Images, Flavors
from .servers_firstgen import FirstGenServers, FirstGenImages
from .exceptions import RackspaceAuthError

class RackspaceSession(object):
    def __init__(self, username=None, api_key=None, region=None, auth_url=None):
        self.session = AuthenticatedSession()
        self.session.login(username, api_key, region, auth_url)

        self.servers = Servers(self.session)
        self.servers.images = Images(self.session)
        self.servers.flavors = Flavors(self.session)
        self.servers_firstgen = FirstGenServers(self.session)
        self.servers_firstgen.images = FirstGenImages(self.session)
        self.domains = Domains(self.session)
        self.domains.records = Records(self.session)
        self.username = username
        self.api_key = api_key
        self.region = region

        # alias the Session verbs here too
        self.get = self.session.get
        self.put = self.session.put
        self.post = self.session.post
        self.delete = self.session.delete
