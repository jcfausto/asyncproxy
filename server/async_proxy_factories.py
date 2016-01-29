#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
from twisted.web.http import HTTPFactory
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.python import log


class AsyncProxyFactory(HTTPFactory):
    """Factory responsible for creating the custom proxy protocols"""
    bytes_transferred = 0


class AsyncProxyClient(Protocol):
    connectedClient = None

    def connectionMade(self):
        self.factory.request.channel.connectedRemote = self
        self.factory.request.setResponseCode(200, "CONNECT OK")
        self.factory.request.setHeader('X-Connected-IP',
                                       self.transport.realAddress[0])
        self.factory.request.setHeader('Content-Length', '0')
        self.factory.request.finish()

    def connectionLost(self, reason):
        if self.connectedClient is not None:
            self.connectedClient.transport.loseConnection()
        log.msg("{bytes} bytes transferred from {remote} to origin (client)".format(remote=self.factory.host,
                                                           bytes=self.factory.bytes_transferred))

    def dataReceived(self, data):
        if self.connectedClient is not None:
            # Forward all bytes from the remote server back to the
            # original connected client
            self.connectedClient.transport.write(data)
            log.msg('%d bytes transferred to origin (client)' % (len(data)))
            # count bytes transferred from remote to the client
            self.factory.bytes_transferred += len(data)
        else:
            pass
            log.msg("UNEXPECTED DATA RECEIVED:", data)


class AsyncProxyClientFactory(ClientFactory):
    protocol = AsyncProxyClient
    bytes_transferred = 0

    def __init__(self, host, port, request):
        self.request = request
        self.host = host
        self.port = port

    def clientConnectionFailed(self, connector, reason):
        self.request.fail("Gateway Error", str(reason))

