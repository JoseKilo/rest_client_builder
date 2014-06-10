REST client
===========

A parameterisable REST HTTP API client.

This is a tool to quickly build REST clients in Python from a list of URL mappings.
It is geared towards mapping client methods to URL names from Django URL patterns.


The workflow for building a custom API client is:

 * Use a command for dumping the mapping of URL names to URLs (including namespacing)
 * Package together the dumped endpoint mapping with an otherwise generic client
 * Distribute
