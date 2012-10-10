# rscloud

## Simple Rackspace API wrapper

Wrap the various Rackspace cloud APIs into an easy to use library. This aims
to keep the interface as close to the actual REST API as possible. The rscloud
methods all operate on, and return the same raw JSON used in the API calls, so
the Rackspace documentation can be as a reference for this library.

Documentation can be found at <http://docs.rackspace.com/api/>


## examples
```python
>>> import rscloud
>>> rs = rscloud.RackspaceSession()

>>> #list firstgen servers
>>> rs.servers_firstgen.list()
u'servers': [{u'id': 503815, u'name': u'srv01'},
 {u'id': 534128, u'name': u'srv02'},
 {u'id': 536526, u'name': u'srv03'},
 {u'id': 537179, u'name': u'srv04'}]}

>>> #list nextgen images supplied by Rackspace
>>> rs.servers.images.list(image_type='BASE')
 u'images': [{u'id': u'acf05b3c-5403-4cf0-900c-9b12b0db0644',
  u'links': [{u'href': u'https://ord.servers.api.rackspacecloud.com/v2/516116/images/acf05b3c-5403-4cf0-900c-9b12b0db0644',
    u'rel': u'self'},
   {u'href': u'https://ord.servers.api.rackspacecloud.com/516116/images/acf05b3c-5403-4cf0-900c-9b12b0db0644',
    u'rel': u'bookmark'},
   {u'href': u'https://ord.images.api.rackspacecloud.com/516116/images/acf05b3c-5403-4cf0-900c-9b12b0db0644',
    u'rel': u'alternate',
    u'type': u'application/vnd.openstack.image'}],
  u'name': u'CentOS 5.8'},
  ...

>>> #create a server named "test01"
>>> rs.servers.create('test01', 'acf05b3c-5403-4cf0-900c-9b12b0db0644', 4)

```

