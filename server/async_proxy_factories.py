#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#


from twisted.web.http import HTTPFactory
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.python import log
import statistics

# imports to properly format the output for statistics
import time
from datetime import timedelta


class AsyncProxyFactory(HTTPFactory):
    """Factory responsible for creating the custom proxy protocols"""
    _startup_time = time.time()

    def update_usage(self, bytes_transferred):
        """
        Updates the accounting for proxy usage (bytes transferred)
        :param bytes_transferred: Some amount of bytes expressed as an int value
        :return: None
        """
        statistics.bytes_transferred += bytes_transferred

    def get_bytes_transferred(self, output_format):
        """
        :param output_format: indicates the desired output format: B, KB or MB.
        :return: The rate of bytes transferred through the proxy in the indicated format.
        """
        return statistics.get_bytes_transferred(output_format)

    def get_uptime(self):
        """
        This function returns the time elapsed since the proxy server startup
        :return: Formatted uptime in N days HH:MM:SS
        """
        delta = timedelta(seconds=time.time() - self._startup_time)
        return ('%d days' % delta.days) + ', ' + time.strftime('%H:%M:%S', time.gmtime(delta.seconds))


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

    def dataReceived(self, data):
        if self.connectedClient is not None:
            # Forward all bytes from the remote server back to the
            # original connected client
            self.connectedClient.transport.write(data)
            log.msg('%d bytes transferred to origin (client)' % (len(data)))
            # count bytes transferred from remote to the client in HTTPS connections
            if self.factory.request.method == 'CONNECT':
                data_size = len(data)
                self.factory.update_usage(data_size)
        else:
            pass
            log.msg("UNEXPECTED DATA RECEIVED:", data)


class AsyncProxyClientFactory(ClientFactory):
    protocol = AsyncProxyClient

    def update_usage(self, bytes_transferred):
        """
        Updates the accounting for proxy usage (bytes transferred)
        :param bytes_transferred: Some amount of bytes expressed as an int value
        :return: None
        """
        statistics.bytes_transferred += bytes_transferred

    def get_bytes_transferred(self, output_format):
        """
        :param output_format: indicates the desired output format: B, KB or MB.
        :return: The rate of bytes transferred through the proxy in the indicated format.
        """
        return statistics.get_bytes_transferred(output_format)

    def __init__(self, host, port, request):
        self.request = request
        self.host = host
        self.port = port

    def clientConnectionFailed(self, connector, reason):
        self.request.fail("Gateway Error", str(reason))

