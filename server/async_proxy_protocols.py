#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
from twisted.web.proxy import Proxy, ProxyRequest
from server.async_proxy_factories import AsyncProxyClientFactory
from twisted.python import log
import urlparse


class AsyncProxyRequestHandler(ProxyRequest):
    """HTTP ProxyRequest handler (factory) that supports CONNECT"""

    connectedProtocol = None

    def process(self):
        if (self.method == 'GET') and (self.uri == '/stats'):
            self.serve_statistics()
        elif self.method == 'CONNECT':
            self.processConnectRequest()
        else:
            ProxyRequest.process(self)

    def fail(self, message, body):
        self.setResponseCode(501, message)
        self.responseHeaders.addRawHeader("Content-Type", "text/html")
        self.write(body)
        self.finish()

    def splitHostPort(self, hostport, default_port):
        port = default_port
        parts = hostport.split(':', 1)
        if len(parts) == 2:
            try:
                port = int(parts[1])
                host = parts[0]
            except ValueError:
                pass

        return host, port

    def processConnectRequest(self):
        parsed = urlparse.urlparse(self.uri)
        default_port = self.ports.get(parsed.scheme)

        host, port = self.splitHostPort(parsed.netloc or parsed.path,
                                        default_port)

        if port == '8080' and host == 'localhost':
            return

        if port is None:
            self.fail("Bad CONNECT Request",
                      "Unable to parse port from URI: %s" % repr(self.uri))
            return

        client_factory = AsyncProxyClientFactory(host, port, self)

        self.reactor.connectTCP(str(host), port, client_factory)

    def serve_statistics(self):
        self.setResponseCode(200)
        self.responseHeaders.addRawHeader("Content-Type", "text/html")
        body = "<html><head></head><body><h1>statistics<br /><h2>Uptime:</h2><p>None</p><h2>Bytes transferred:</h2><p>{bytes_transferred}</p></h1></body></html>".format(
                bytes_transferred='1024')
        self.write(body)
        self.finish()


class AsyncProxyChannel(Proxy):
    """HTTP Server Protocol that supports CONNECT"""
    requestFactory = AsyncProxyRequestHandler
    connectedRemote = None

    def requestDone(self, request):
        if ((request.method != 'CONNECT') and ('content-length' in request.headers)):
            log.msg('Content-Length: %d' % int(request.headers['content-length']))

        if request.method == 'CONNECT' and self.connectedRemote is not None:
            self.connectedRemote.connectedClient = self
        else:
            Proxy.requestDone(self, request)

    def connectionLost(self, reason):
        if self.connectedRemote is not None:
            self.connectedRemote.transport.loseConnection()
        Proxy.connectionLost(self, reason)

    def dataReceived(self, data):
        if self.connectedRemote is None:
            log.msg('%d bytes received from origin (client)' % (len(data)))
            Proxy.dataReceived(self, data)
        else:
            # Once proxy is connected, forward all bytes received
            # from the original client to the remote server.
            self.connectedRemote.transport.write(data)
            log.msg('%d bytes transferred to destination (remote)' % (len(data)))