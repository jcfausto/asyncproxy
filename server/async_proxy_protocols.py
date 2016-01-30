#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#


import urlparse

from twisted.web.proxy import Proxy, ProxyRequest
from twisted.python import log

from server.async_proxy_factories import AsyncProxyClientFactory
from server.statistics import _BytesTransferedOutputFormat


class AsyncProxyRequestHandler(ProxyRequest):
    """HTTP ProxyRequest handler (factory) that supports CONNECT"""

    connectedProtocol = None

    def process(self):
        header_has_range_parameter = self.requestHeaders.hasHeader('range')
        request_has_range_query_parameter = 'bytes' in self.args

        if (header_has_range_parameter and request_has_range_query_parameter):
            header_range_value = self.requestHeaders._rawHeaders['range'][0]
            request_range_value = self.args['bytes'][0]
            if (header_range_value != request_range_value):
                self.fail('Requested Range not satisfiable',
                          """<!DOCTYPE html><head><title>AsyncProxy - 416: Requested Range not satisfiable</title>
                          </head><body>The values of header range and query range parameter differ: Header: {header},
                          Query: {query}</body></html>""".format(header=str(header_range_value),
                                                                 query=str(request_range_value)), 416)
                return


        if (self.method == 'GET') and (self.uri == '/stats'):
            self.serve_statistics()
            #self.redirect("".join(str(self.host.host) + ':' + str(os.environ.get('ASYNC_PROXY_STATS_PORT', 8081)) + '/stats'))
            self.finish()
        elif self.method == 'CONNECT':
            self.processConnectRequest()
        else:
            ProxyRequest.process(self)

    def fail(self, message, body, status=501):
        self.setResponseCode(status, message)
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
        body = """<!DOCTYPE html>
                <html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1">
                <!-- Latest compiled and minified CSS -->
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css"
                integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7"
                crossorigin="anonymous"></head>
                    <body>
                        <div class="container">
                            <div class="page-header">
                                <h1>AsyncProxy <small>statistics</small></h1>
                            </div>
                            <div class="row">
                                <div class="col-sm-6 col-md-6">
                                    <div class="panel panel-primary">
                                        <div class="panel-heading">Uptime</div>
                                        <div class="panel-body"><center><h2>{uptime}</center></h2></div>
                                    </div>
                                </div>
                                <div class="col-sm-6 col-md-6">
                                    <div class="panel panel-success">
                                        <div class="panel-heading">Bytes transferred</div>
                                        <div class="panel-body"><center><h2>{bytes_transferred}</h2></center></div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6 col-md-6">
                                    <div class="panel panel-info">
                                        <div class="panel-heading">KBytes transferred</div>
                                        <div class="panel-body"><center><h2>{kbytes_transferred}</center></h2></div>
                                    </div>
                                </div>
                                <div class="col-sm-6 col-md-6">
                                    <div class="panel panel-info">
                                        <div class="panel-heading">MBytes transferred</div>
                                        <div class="panel-body"><center><h2>{mbytes_transferred}</center></h2></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </body>
                </html>""".format(uptime=self.channel.factory.get_uptime(),
                                  bytes_transferred=self.channel.factory.get_bytes_transferred(_BytesTransferedOutputFormat().BYTES),
                                  kbytes_transferred=self.channel.factory.get_bytes_transferred(_BytesTransferedOutputFormat().KBYTES),
                                  mbytes_transferred=self.channel.factory.get_bytes_transferred(_BytesTransferedOutputFormat().MBYTES))
        self.write(body)
        self.finish()


class AsyncProxyChannel(Proxy):
    """Proxy that resides between the cliente and the remote."""
    requestFactory = AsyncProxyRequestHandler
    connectedRemote = None

    def requestDone(self, request):
        if ((request.method != 'CONNECT') and ('content-length' in request.headers)):
            log.msg('Content-Length: %d' % int(request.headers['content-length']))
            self.factory.update_usage(request.sentLength)

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