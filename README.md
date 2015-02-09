REST Client Builder
===================

A tool to generate REST HTTP API clients for Django projects.

This is a tool to quickly build REST clients in Python from a list of URL mappings.
It is geared towards mapping client methods to URL names from Django URL patterns.


The workflow for building a custom API client is:

 * Use a command for dumping the mapping of URL names to URLs (including namespacing)
 * Package together the dumped endpoint mapping with an otherwise generic client
 * Distribute


To run tests
-------------------
* And test requirements if you want to run tests
    pip install -r test-requirements.txt
* Run nose command
    nosetests


Client code example
-------------------

In order to consume an API endpoint like

``GET http://www.myhost.com/api/resource/sub-resource?name=res1``

The user code will be:

``
my_sub_resource = Client(host, credentials).resource.sub_resource(name='res1')
``

Names for above python accesible objects will be taken from url names and
namespaces specified on urls.py modules found in your Django API server
project.

For example, if your project has an urlpattern like this:

``
url(
    regex=r'^my-url-pattern/',
    view=views.my_view,
    name='my-name'
)
``

The equivalent Python expression would be:

``
client = Client('http://www.my-domain.com/api/', 'MyUsername', 'MyPassword')
result = client.my_name()
``

Note that hyphens (``-``) are replaced by underscores (``_``).

You can also include custon headers. To do that, just provide a ``dict``
containing them, example:

```
headers = {
    'header1': 'value1',
    'header2': 'value2',
}
client = Client('http://www.my-domain.com/api/', headers=headers)
```

Also the SSL cert verification can be switched using the ``verify`` parameter. It
can be ``True`` or ``False``:

```
client = Client('http://www.my-domain.com/api/', verify=False)
```

Client library generation
-------------------------

Include `rest_client_builder` into your requirements.

Include ``rest_client`` into ``INSTALLED_APPS`` of your Django API server project.

Run the following management command:

``python manage.py generate_api_client [path/to/your/root/api/urls.py]``

It will package your client library and will place it inside

``_rest_client_build/``

You can then install it on your client-side project.
