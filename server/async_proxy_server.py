#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
import os
from twisted.application import internet, service
from server.async_proxy_factories import AsyncProxyFactory
from server.async_proxy_protocols import AsyncProxyChannel

# To serve statistics
from twisted.web import server
from server.statistics import AsyncProxyStatistics

"""
The basic steps to create a twisted application are:
  - Create the application that will contain the services.
  - Create the service instance.
  - Register the server into the application by setting the application
    as the service parent.

To generate self-signed certificates for test purposes:
$ openssl req -new -x509 -nodes -out server.pem -keyout server.key -days 3650 -subj '/CN=localhost'
Generating a 1024 bit RSA private key

To run:
twistd --nodaemon --python  server/async_proxy_server.py
twistd --debug --python  server/async_proxy_server.py

To change the port where the proxy will listen set up a env var
export ASYNC_PROXY_SERVER_PORT=5000
"""

async_proxy_server_port = int(os.environ.get('ASYNC_PROXY_SERVER_PORT', 8000))

application = service.Application('AsyncProxy')
service_collection = service.IServiceCollection(application)

custom_factory = AsyncProxyFactory()
custom_factory.protocol = AsyncProxyChannel

async_proxy_service_tcp = internet.TCPServer(async_proxy_server_port, custom_factory)

root = AsyncProxyStatistics()

# TODO Give some style to statistics...
#root.putChild('styles', static.File("./public/css"))

site = server.Site(root)
web_server = internet.TCPServer(8081, site)

async_proxy_service_tcp.setServiceParent(service_collection)
web_server.setServiceParent(service_collection)

