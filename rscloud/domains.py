#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

import json


class Domains(object):
    def __init__(self, session):
        """
        Rackspace Domains API

        :param session: rscloud.AuthenticatedSession
        """
        self._sess = session
        self._url = session.sc['cloudDNS']['publicURL'] + '/domains'

    def list(self, domain_name=None):
        if domain_name:
            params = {'name': domain_name}
        else:
            params = None
        resp = self._sess.get(self._url, params=params)
        return resp.json

    def list_subdomains(self, domain_id):
        url = self._url + '/' + str(domain_id) + '/subdomains'
        resp = self._sess.get(url)
        return resp.json

    def detail(self, domain_id, records=True, subdomains=False):
        url = self._url + '/' + str(domain_id)
        params = {'showRecords': str(bool(records)).lower(),
                  'showSubdomains': str(bool(subdomains)).lower()}

        resp = self._sess.get(url, params=params)
        return resp.json

    def changes(self, domain_id, since=None):
        url = self._url + '/' + str(domain_id) + '/changes'
        params = {}
        if since:
            params['since'] = since

        resp = self._sess.get(url, params=params)
        return resp.json

    def export(self, domain_id):
        url = self._url + '/' + str(domain_id) + '/export'
        resp = self._sess.get(url)
        return resp.json

    def create(self, domain_records):
        # async with callback
        # TODO: make it easier to specify domain records
        body = json.dumps(domain_records)
        resp = self._sess.post(self._url, data=body)
        return resp.json

    def import_domains(self, records):
        # async with callback
        url = self._url + '/import'
        # contents must be bind_9 records
        if isinstance(records, basestring):
            records = [records]

        domains = []
        for rec in records:
            domains.append({'contentType': 'BIND_9', 'contents': rec})

        body = json.dumps({'domains': domains})

        resp = self._sess.post(url, data=body)
        return resp.json

    def modify(self, domain_id, email, ttl, comment):
        # async with callback
        url = self._url + '/' + str(domain_id)
        body = {'comment': comment,
                'emailAddress': email,
                'ttl': int(ttl),
                }

        resp = self._sess.put(url, data=json.dumps(body))
        return resp.json

    def remove(self, domain_ids, subdomains=False):
        # async with callback
        assert isinstance(domain_ids, (list, tuple))
        params = {}
        if len(domain_ids) == 1:
            url = self._url + '/' + str(domain_ids[0])
        else:
            url = self._url
            params['id'] = domain_ids

        if subdomains:
            params['deleteSubdomains'] = 'true'

        resp = self._sess.delete(url, params=params)
        return resp.json


class Records(object):
    def __init__(self, session):
        self._sess = session
        self._url = session.sc['cloudDNS']['publicURL'] + '/domains'

    def list(self, domainId):
        url = self._url + '/' + str(domainId) + '/records'
        resp = self._sess.get(url)
        return resp.json

    def search(self, domainId, record_type='A', name=None, data=None):
        url = self._url + '/' + str(domainId) + '/records'
        params = {
            'type': record_type,
            'name': name,
            'data': data,
        }
        resp = self._sess.get(url, params=params)
        return resp.json

    def detail(self, domainId, recordId):
        url = self._url + '/' + str(domainId) + '/records/' + str(recordId)
        resp = self._sess.get(url)
        return resp.json

    def add(self, domainId, name, data, record_type, priority=None,
            ttl=None, comment=None):
        #TODO: add multiple records
        url = self._url + '/' + str(domainId) + '/records'
        record = {
            'name': name,
            'type': record_type,
            'data': data,
        }
        if priority:
            record['priority'] = priority
        if ttl:
            record['ttl'] = ttl
        if comment:
            record['comment'] = comment

        req_data = json.dumps({'records': [record]})

        resp = self._sess.post(url, data=req_data)
        return resp.json

    def remove(self, domainId, recordId):
        url = self._url + '/' + str(domainId) + '/records/' + str(recordId)
        resp = self._sess.delete(url)
        return resp.json

    def modify(self, domainId, recordId, name=None, data=None,
               priority=None, comment=None):
        url = self._url + '/' + str(domainId) + '/records/' + str(recordId)
        record_data = {}
        if name:
            record_data['name'] = name
        if data:
            record_data['data'] = data
        if priority:
            record_data['priority'] = priority
        if comment:
            record_data['comment'] = comment

        req_data = json.dumps(record_data)
        resp = self._sess.put(url, data=req_data)
        return resp.json


class Rdns(object):
    def __init__(self, session):
        self._sess = session
