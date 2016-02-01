#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#

"""
# Uncomment this if you want to run in pyCharm for example.


from twisted.python import log

from server.async_proxy_factories import AsyncProxyFactory
from server.async_proxy_protocols import AsyncProxyChannel

if __name__ == '__main__':
    import sys

    log.startLogging(sys.stderr)

    factory = AsyncProxyFactory()
    factory.protocol = AsyncProxyChannel

    import twisted.internet

    twisted.internet.reactor.listenTCP(8000, factory)

    twisted.internet.reactor.run()
    
"""    



