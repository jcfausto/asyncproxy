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

"""
The basic steps to create a twisted application are:
  - Create the application that will contain the services.
  - Create the service instance.
  - Register the server into the application by setting the application
    as the service parent.

To run:
twistd --nodaemon --python=server/async_proxy_server.py

To change the port where the proxy will listen set up a env var
export ASYNC_PROXY_SERVER_PORT=5000

default docker address 192.168.99.100
"""

async_proxy_server_port = int(os.environ.get('ASYNC_PROXY_SERVER_PORT', 8000))

application = service.Application('AsyncProxy')
service_collection = service.IServiceCollection(application)

custom_factory = AsyncProxyFactory()
custom_factory.protocol = AsyncProxyChannel

async_proxy_service_tcp = internet.TCPServer(async_proxy_server_port, custom_factory)
async_proxy_service_tcp.setServiceParent(service_collection)
