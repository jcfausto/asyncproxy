from twisted.web import resource


class AsyncProxyStatistics(resource.Resource):
    isLeaf = False

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.geChild(self, name, request)

    def render_GET(self, request):
        return "<html>Statistics</html>"


