from subprocess import call

call(["twistd", "--nodaemon", "--python=async_proxy_server.py"])


"""
from twisted.python import log

from server.async_proxy_factories import AsyncProxyFactory
from server.async_proxy_protocols import AsyncProxyChannel

if __name__ == '__main__':
    import sys

    log.startLogging(sys.stderr)

    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('port', default=8080, nargs='?', type=int)
    ap.add_argument('--ssl-cert', type=str)
    ap.add_argument('--ssl-key', type=str)
    ns = ap.parse_args()

    factory = AsyncProxyFactory()
    factory.protocol = AsyncProxyChannel

    import twisted.internet

    if ns.ssl_key and not ns.ssl_cert:
        log.msg("--ssl-key must be used with --ssl-cert")
        sys.exit(1)
    if ns.ssl_cert:
        from twisted.internet import ssl

        with open(ns.ssl_cert, 'rb') as fp:
            ssl_cert = fp.read()
        if ns.ssl_key:
            from OpenSSL import crypto

            with open(ns.ssl_key, 'rb') as fp:
                ssl_key = fp.read()
            certificate = ssl.PrivateCertificate.load(
                    ssl_cert,
                    ssl.KeyPair.load(ssl_key, crypto.FILETYPE_PEM),
                    crypto.FILETYPE_PEM)
        else:
            certificate = ssl.PrivateCertificate.loadPEM(ssl_cert)
        twisted.internet.reactor.listenSSL(ns.port, factory,
                                           certificate.options())
    else:
        twisted.internet.reactor.listenTCP(ns.port, factory)
    twisted.internet.reactor.run()

"""