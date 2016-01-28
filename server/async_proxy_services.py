#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
from twisted.application import internet


class AsyncProxyServiceTCP(internet.TCPServer):

    def __init__(self, port, factory):
        super().__init__(port, factory)


class AsyncProxyServiceSSL(internet.SSLServer):

    def __init__(self, port, factory, context_factory):
        super().__init__(port, factory, context_factory)