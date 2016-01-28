#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
from twisted.application import service, internet
from twisted.internet import ssl

from server.async_proxy_factories import AsyncProxyFactory
from server.async_proxy_protocols import AsyncProxyChannel
from server.async_proxy_services import AsyncProxyServiceTCP, AsyncProxyServiceSSL

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

"""

application = service.Application('AsyncProxy')

custom_factory = AsyncProxyFactory()
custom_factory.protocol = AsyncProxyChannel

async_proxy_service_tcp = AsyncProxyServiceTCP(8080, custom_factory)
#async_proxy_service_ssl = AsyncProxyServiceSSL(443, custom_factory,
#                                               ssl.DefaultOpenSSLContextFactory('ssl-ssl-keys/server.key',
#                                                                                'ssl-ssl-keys/server.pem'))

async_proxy_service_tcp.setServiceParent(application)
#async_proxy_service_ssl.setServiceParent(application)
