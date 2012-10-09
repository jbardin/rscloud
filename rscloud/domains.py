#!/usr/bin/env python
# Copyright 2012 litl, LLC. All Rights Reserved.

import json

class Domains(object):
    def __init__(self, session):
        """
        Rackspace Domains API

        :param session: authenticated requests session
        """
        self._sess = session
        self.url = session.sc['cloudDNS']['publicURL']

    def list(self, domain_name=None):
        if domain_name:
            params = {'name': domain_name}
        else:
            params = None
        resp = self._sess.get(self.url, params=params)
        return resp.json

    def list_subdomains(self, domain_id):
        url = self.url + '/' + str(domain_id) + '/subdomains'
        resp = self._sess.get(url)
        return resp.json

    def detail(self, domain_id, records=True, subdomains=False):
        url = self.url + '/' + str(domain_id)
        params = {'showRecords': str(bool(records)).lower(),
                    'showSubdomains': str(bool(subdomains)).lower()
                    }

        resp = self._sess.get(url, params=params)
        return resp.json

    def changes(self, domain_id, since=None):
        url = self.url + '/' + str(domain_id) + '/changes'
        if since:
            params = {'since': since.isoformat()}

        resp = self._sess.get(url, params=params)
        return resp.json

    def export(self, domain_id):
        url = self.url + '/' + str(domain_id) + '/export'
        resp = self._sess.get(url)
        return resp.json

    def create(self, domain_records):
        # async with callback
        # TODO: make it easier to specify domain records
        body = json.dumps(domain_records)
        resp = self._sess.post(self.url, data=body)
        return resp.json

    def import_domains(self, records):
        # async with callback
        url = self.url + '/import'
        # contents must be bind_9 records
        if isinstance(records, basestring):
            records = [records]

        domains = []
        for rec in records:
            domains.append({'contentType': 'BIND_9', 'contents': rec})

        body = jdon.dumps({'domains': domains})

        resp = self._sess.post(url, data=body)
        return resp.json

    def modify(self, domain_id, email, ttl, comment):
        # async with callback
        url = self.url + '/' + str(domain_id)
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
            url = self.url + '/' + str(domain_ids[0])
        else:
            url = self.url
            params['id'] = domain_ids

        if subdomains:
            params['deleteSubdomains'] = 'true'

        resp = self._sess.delete(url, params=params)
        return resp.json


class Records(object):
    def __init__(self, session):
        self._sess = session
        self.url = session.sc['cloudDNS']['publicURL']

    def get_record_from_name(self, name):
        pass

    def list(self, domain_id):
        pass


class Rdns(object):
    def __init__(self, session):
        self._sess = session


