#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

import json


class FirstGenServers(object):
    def __init__(self, session):
        """
        Rackspace Coudservers First Gen API

        :param session: rscloud.AuthenticatedSession
        """
        self._sess = session
        self.url = session.sc['cloudServers']['publicURL'] + '/servers'

    def create(self, name, image, flavor, personality=None):
        """
        Create a cloud server.

        :param name: server name
        :param image: id of base image
        :param flavor: id number of desired flavor
        :param personality: personality to be injected into the new server.
            defaults to None
        """
        if personality is None:
            personality = []

        req_body = {'server': {'name': name,
                               'imageId': image,
                               'flavorId': flavor,
                               'personality': personality}
                    }

        resp = self._sess.post(self.url, data=json.dumps(req_body))
        return resp.json

    def delete(self, server_id):
        """
        Delete a cloud server

        :param server_id: numerical id of the server to be deleted
        """
        url = self.url + '/' + str(server_id)
        resp = self._sess.delete(url)
        return resp.json

    def list(self):
        """
        List all cloud servers
        """
        resp = self._sess.get(self.url)
        return resp.json

    def detail(self, server_id=None):
        """
        List details of cloud servers

        :param server_id: id of server to detail. If server_id is None, detail
            all servers.
        """
        if not server_id:
            url = self.url + '/detail'
        else:
            url = self.url + '/' + str(server_id)

        resp = self._sess.get(url)
        return resp.json


class FirstGenImages(object):
    def __init__(self, session):
        """
        Rackspace Coudservers First Gen API

        :param session: rscloud.AuthenticatedSession
        """
        self._sess = session
        self.url = session.sc['cloudServers']['publicURL'] + '/images'

    def detail(self, image_id):
        """
        Retreive details of a server image

        :param server_id: numerical id of image to detail
        """
        url = self.url + '/' + str(image_id)
        resp = self._sess.get(url)
        return resp.json

    def list(self):
        """
        List all server images
        """
        resp = self._sess.get(self.url)
        return resp.json

    def create(self, server_id, name):
        """
        Create a new server image

        :param server_id: numerical id of server to image
        :param name: name for new image
        """
        req_body = {'image': {'serverId': int(server_id),
                              'name': name}
                    }

        resp = self._sess.post(self.url, data=json.dumps(req_body))
        return resp.json

    def delete(self, image_id):
        """
        Delete a server image

        :param image_id: numerical id of image to delete
        """
        url = self.url + '/' + str(image_id)
        resp = self._sess.delete(url)
        return resp.json
