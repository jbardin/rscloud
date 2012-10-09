#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

import json
import time

class Servers(object):
    def __init__(self, session):
        """
        Rackspace Coudservers Next Gen API

        :param session: rscloud.AuthenticatedSession
        """
        self._sess = session
        self._url = session.sc['cloudServersOpenStack']['publicURL'] + '/servers'

    def create(self, name, imageRef, flavorRef, personality=None,
               metadata=None, async=True):
        """
        Create a cloud server.

        :param name: server name
        :param image: id of base image
        :param flavor: id number of desired flavor
        :param metadata: key/value metadata
        :param personality: files to be injected into the new server
        """
        if personality is None:
            personality = []

        req_body = {'server': {
                        'name': name,
                        'imageRef': imageRef,
                        'flavorRef': flavorRef,
                        'metadata': metadata,
                        'personality': personality,
                        }
                    }

        resp = self._sess.post(self._url, data=json.dumps(req_body))
        print resp

        if async:
            return resp.json
        else:
            return self._wait_for_server(resp.json)

    def delete(self, server_id):
        """
        Delete a cloud server

        :param server_id: numerical id of the server to be deleted
        """
        url = self._url + '/' + server_id
        resp = self._sess.delete(url)
        return resp.json

    def list(self, image=None, flavor=None, name=None, status=None,
             marker=None, limit=None, changes_since=None, detail=False):
        """
        List all cloud servers
        """
        if detail:
            url = self._url + '/detail'
        else:
            url = self._url

        params = {'image': image,
                  'flavor': flavor,
                  'name': name,
                  'status': status,
                  'marker': marker,
                  'limit': limit,
                  'changes-since': changes_since}

        resp = self._sess.get(url, params=params)
        return resp.json

    def detail(self, server_id):
        """
        List details of cloud server
        """
        url = self._url + '/' + server_id
        resp = self._sess.get(url)
        return resp.json

    def update(self):
        raise NotImplementedError

    def action(self):
        raise NotImplementedError

    def _wait_for_server(self, resp):
        # this is only returned once, so don't lose it!
        admin_pass = resp['server']['adminPass']
        status = 'BUILD'
        progress = 0
        link = None
        for each in resp['server']['links']:
            if each['rel'] == 'self':
                link = each['href']

        # TODO: error checking for the responses

        while status == 'BUILD':
            time.sleep(5)

            resp = self._sess.get(link)
            status = resp.json['server']['status']
            progress = resp.json['server']['progress']
            # TODO: log progress

        server_detail = resp.json.copy()
        server_detail['adminPass'] = admin_pass
        return server_detail


class Images(object):
    def __init__(self, session):
        """
        Rackspace Coudservers Images

        :param session: rscloud.AuthenticatedSession
        """
        self._sess = session
        self._url = session.sc['cloudServersOpenStack']['publicURL'] + '/images'

    def detail(self, image_id):
        """
        Retreive details of a server image

        :param server_id: numerical id of image to detail
        """
        url = self._url + '/' + image_id
        resp = self._sess.get(url)
        return resp.json

    def list(self, server=None, name=None, status=None, changes_since=None,
             marker=None, limit=None, image_type=None):
        """
        List all server images

        :param server: Filters the list of images by server.
                       Specify the server reference by ID or by full URL
        :param name: Filters the list of images by image name
        :param status: Filters the list of images by status
        :param changes_since: Filter images to those with change since time
        :param marker: The ID of the last item in the previous list
        :param limit: page size
        :param image_type: Filter Rackspace images, or client images (BASE|SERVER)
        """
        params = {'server': server,
                  'name': name,
                  'status': status,
                  'changes-since': changes_since,
                  'marker': marker,
                  'limit': limit,
                  'type': image_type}

        resp = self._sess.get(self._url, params=params)
        return resp.json

    def create(self, server_id, name):
        """
        Create a new server image

        :param server_id: numerical id of server to image
        :param name: name for new image
        """
        req_body = {'image': {
                        'serverId': int(server_id),
                        'name': name
                        }
                    }

        resp = self._sess.post(self._url, data=json.dumps(req_body))
        return resp.json

    def delete(self, image_id):
        """
        Delete a server image

        :param image_id: numerical id of image to delete
        """
        url = self._url + '/' + image_id
        resp = self._sess.delete(url)
        return resp.json
