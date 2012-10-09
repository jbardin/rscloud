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
        self._url = (session.sc['cloudServersOpenStack']['publicURL'] +
                     '/servers')

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

        req_body = {'server': {'name': name,
                               'imageRef': imageRef,
                               'flavorRef': str(flavorRef),
                               'metadata': metadata,
                               'personality': personality}
                    }

        resp = self._sess.post(self._url, data=json.dumps(req_body))

        if async:
            return resp.json
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

        params = {}
        if image:
            params['image'] = image
        if flavor:
            params['flavor'] = flavor
        if name:
            params['name'] = name
        if status:
            params['status'] = status
        if marker:
            params['marker'] = marker
        if limit:
            params['limit'] = limit
        if changes_since:
            params['changes-since'] = changes_since
        if detail:
            params['detail'] = detail

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

    def changePassword(self, serverId, password):
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'changePassword': {'adminPass': password}})
        resp = self._sess.post(url, data=data)
        return resp.json

    def reboot(self, serverId, reboot_type='SOFT'):
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'reboot': {'type': reboot_type}})
        resp = self._sess.post(url, data=data)
        return resp.json

    def rebuild(self, name, imageRef, flavorRef, personality=None,
                metadata=None, async=True):
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'rebuild': {'name': name,
                                       'imageRef': imageRef,
                                       'flavorRef': str(flavorRef),
                                       'metadata': metadata,
                                       'personality': personality}
                           })
        resp = self._sess.post(url, data=data)
        if async:
            return resp.json
        return self._wait_for_server(resp.json)

    def resize(self, serverId, flavorId):
        # API bug, resize.flavorRef only accepts flavorId
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'resize': {
                           'flavorRef': str(flavorId)}
                           })
        resp = self._sess.post(url, data=data)
        return resp.json

    def confirmResize(self, serverId):
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'confirmResize': None})
        resp = self._sess.post(url, data=data)
        return resp.json

    def revertResize(self, serverId):
        #TODO: can this be async?
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'revertResize': None})
        resp = self._sess.post(url, data=data)
        return resp.json

    def rescue(self, serverId):
        # TODO: make a synchronous option
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'rescue': "none"})
        resp = self._sess.post(url, data=data)
        return resp.json

    def unrescue(self, serverId):
        # TODO: make a synchronous option
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'unrescue': None})
        resp = self._sess.post(url, data=data)
        return resp.json

    def createImage(self, serverId, name, metadata):
        # TODO, wait for something
        url = self._url + '/' + serverId + '/action'
        data = json.dumps({'createImage': {'name': name,
                                           'metadata': metadata}
                           })
        resp = self._sess.post(url, data=data)
        return resp.json

    def _wait_for_server(self, resp):
        # TODO: timeout
        # this is only returned once, so don't lose it!
        admin_pass = resp['server'].get('adminPass')
        status = 'WAIT'
        progress = 0
        link = None
        for each in resp['server']['links']:
            if each['rel'] == 'self':
                link = each['href']

        # TODO: error checking for the responses

        while status in ('WAIT', 'BUILD', 'REBUILD', 'RESIZE'):
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
        self._url = (session.sc['cloudServersOpenStack']['publicURL']
                     + '/images')

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
        :param image_type: Filter Rackspace or client images (BASE|SERVER)
                           !SERVER type does not currently work!
        """
        params = {}
        if server:
            params['server'] = server
        if name:
            params['name'] = name
        if status:
            params['status'] = status
        if changes_since:
            params['changes-since'] = changes_since
        if marker:
            params['marker'] = marker
        if limit:
            params['limit'] = limit
        if image_type:
            params['type'] = image_type

        resp = self._sess.get(self._url, params=params)
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

        resp = self._sess.post(self._url, data=json.dumps(req_body))
        return resp.json

    def delete(self, image_id):
        """
        Delete a server image

        :param image_id: id of image to delete
        """
        url = self._url + '/' + image_id
        resp = self._sess.delete(url)
        return resp.json


class Flavors(object):
    def __init__(self, session):
        """
        Rackspace Coudservers Flavors

        :param session: rscloud.AuthenticatedSession
        """
        self._sess = session
        self._url = (session.sc['cloudServersOpenStack']['publicURL']
                     + '/flavors')

    def list(self, minDisk=None, minRam=None, marker=None, limit=None,
             detail=False):
        """
        List all server flavors

        :param minDisk: Filters the list of flavors to those with the specified
                        minimum number of gigabytes of disk storage.)
        :param minRam: Filters the list of flavors to those with the specified
                       minimum amount of RAM in megabytes.
        :param marker: The ID of the last item in the previous list.
        :param limit: Sets the page size.

        """
        if detail:
            url = self._url + '/detail'
        else:
            url = self._url

        params = {'minDisk': minDisk,
                  'minRam': minRam,
                  'marker': marker,
                  'limit': limit}

        resp = self._sess.get(self._url, params=params)
        return resp.json

    def detail(self, flavor_id):
        """
        Lists details of the specified flavor

        :param flavor_id: id of flavor to detail

        """
        url = self._url + '/' + str(flavor_id)
        resp = self._sess.get(url)
        return resp.json
