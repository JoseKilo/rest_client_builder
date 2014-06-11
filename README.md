REST client builder
===================

A tool to generate REST HTTP API clients for Django projects.

This is a tool to quickly build REST clients in Python from a list of URL mappings.
It is geared towards mapping client methods to URL names from Django URL patterns.


The workflow for building a custom API client is:

 * Use a command for dumping the mapping of URL names to URLs (including namespacing)
 * Package together the dumped endpoint mapping with an otherwise generic client
 * Distribute


Client code example
-------------------

In order to consume an API endpoint like

``GET http://www.myhost.com/api/resource/sub-resource?name=res1``

The user code will be:

``
my_sub_resource = Client().resource.sub_resource(name='res1')
``


Client library generation
-------------------------

Include this app into ``INSTALLED_APPS`` of your Django project.

Run the following management command:

``python manage.py generate_endpoints [path/to/your/root/api/urls.py]``

It will package your client library and will place it inside

``_rest_client_build/``

You can then install it on your client-side project.
