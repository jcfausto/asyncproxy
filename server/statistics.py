#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
from twisted.web import resource


class AsyncProxyStatistics(resource.Resource):
    isLeaf = False

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.geChild(self, name, request)

    def render_GET(self, request):
        return "<html>Statistics</html>"


