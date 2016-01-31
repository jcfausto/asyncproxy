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
from server.statistics import BytesTransferedOutputFormat


class AsyncProxyRequestHandler(ProxyRequest):
    """HTTP ProxyRequest will handle the requests submitted from client to proxy"""

    connectedProtocol = None

    def header_has_range_parameter(self):
        """
        Checks if the header contains the 'range' parameter
        :return: boolean
        """
        return self.requestHeaders.hasHeader('range')

    def request_has_range_query_parameter(self):
        """
        Checks if the query uri contains the 'range' query parameter
        :return: boolean
        """
        return 'bytes' in self.args

    def get_header_range_request_value(self):
        """
        Return the byte range specified in the range parameter in the request's header.
        :return: str
        """
        if self.header_has_range_parameter():
            return str(self.requestHeaders._rawHeaders['range'][0])
        else:
            return '0-0'

    def get_query_range_request_value(self):
        """
        Return the byte range specified in the query range parameter in the request's URI.
        :return: str
        """
        if self.request_has_range_query_parameter():
            return str(self.args['bytes'][0])
        else:
            return '0-0'

    def range_request_satisfiable(self):
        """
        Check if the header and query range request value are equal when both are present.
        Else, return True by default.
        :return: boolean
        """
        hvalue = self.get_header_range_request_value()
        rvalue = self.get_query_range_request_value()
        req_has_parameter = self.request_has_range_query_parameter()
        hea_has_parameter = self.header_has_range_parameter()

        if req_has_parameter and hea_has_parameter:
            return hvalue == rvalue
        else:
            return True

    def statistics_requested(self):
        """
        Check if the request was on the /stats endpoint
        :return: boolean
        """
        return (self.method == 'GET') and (self.uri == '/stats')

    def process(self):

        """
        Checks if a range request was demanded and if its satisfies the requirements.
        If don't, and 416 - Requested Range not satisfiable will the returned in response.
        """
        if not self.range_request_satisfiable():
            error_message = """
                <!DOCTYPE html>
                    <head>
                        <title>AsyncProxy - 416: Requested Range not satisfiable</title>
                    </head>
                    <body>
                        The values of header range and query range parameter differ: Header: {header}, Query: {query}
                    </body>
                </html>""".format(header=self.get_header_range_request_value(),
                                  query=self.get_query_range_request_value())

            self.fail('Requested Range not satisfiable', error_message, 416)

            # Don't remove this return even if your IDE doesn't understand it.
            return

        # Checks to see if the request is for proxy statistics
        if self.statistics_requested():
            self.serve_statistics()
        elif self.method == 'CONNECT':
            # Handling HTTPS requests that comes with a CONNECT request
            self.process_connect_request()
        else:
            ProxyRequest.process(self)

    def fail(self, message, body, status=501):
        self.setResponseCode(status, message)
        self.responseHeaders.addRawHeader("Content-Type", "text/html")
        self.write(body)
        self.finish()

    def split_host_port(self, hostport, default_port):

        """Splits the host and port from the request"""

        port = default_port
        parts = hostport.split(':', 1)
        if len(parts) == 2:
            try:
                port = int(parts[1])
                host = parts[0]
            except ValueError:
                pass

        return host, port

    def process_connect_request(self):

        """Handle HTTPS CONNECT requests"""

        parsed = urlparse.urlparse(self.uri)
        default_port = self.ports.get(parsed.scheme)

        host, port = self.split_host_port(parsed.netloc or parsed.path, default_port)

        if port is None:
            self.fail("Bad CONNECT Request",
                      "Unable to parse port from URI: %s" % repr(self.uri))

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
                                  bytes_transferred=self.channel.factory.get_bytes_transferred(BytesTransferedOutputFormat().BYTES),
                                  kbytes_transferred=self.channel.factory.get_bytes_transferred(BytesTransferedOutputFormat().KBYTES),
                                  mbytes_transferred=self.channel.factory.get_bytes_transferred(BytesTransferedOutputFormat().MBYTES))
        self.write(body)
        self.finish()


class AsyncProxyChannel(Proxy):

    """Proxy that resides between the cliente and the remote."""

    requestFactory = AsyncProxyRequestHandler
    connectedRemote = None

    def requestDone(self, request):

        # Only for non HTTPS connections.
        if (request.method != 'CONNECT') and ('content-length' in request.headers):
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