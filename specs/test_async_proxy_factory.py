#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#


import time
from unittest import TestCase

from server.statistics import BytesTransferedOutputFormat
from server.async_proxy_factories import AsyncProxyFactory


class TestAsyncProxyFactory(TestCase):

    proxy = AsyncProxyFactory

    def setUp(self):
        self.proxy = AsyncProxyFactory()

    def test_bytes_transferred_update_returns_correct_bytes_amount(self):
        """
        Should return the correct amount of bytes after information update.
        """
        self.proxy.update_usage(1024)
        self.assertEqual(self.proxy.get_bytes_transferred(BytesTransferedOutputFormat().BYTES), 1024)


    def test_bytes_transferred_update_returns_correct_kilobytes_amount(self):
        """
        Should return the correct amount of bytes after information update.
        """
        proxy = AsyncProxyFactory()
        proxy.update_usage(1024)
        self.assertEqual(proxy.get_bytes_transferred(BytesTransferedOutputFormat().KBYTES), 2)

    def test_bytes_transferred_update_returns_correct_megabytes_amount(self):
        """
        Should return the correct amount of bytes after information update.
        """
        proxy = AsyncProxyFactory()
        proxy.update_usage(2300000)
        self.assertEqual(proxy.get_bytes_transferred(BytesTransferedOutputFormat().MBYTES), 2.195404052734375)

    def test_should_return_10_seconds_as_uptime(self):
        """
        Should return the correct uptime
        """
        proxy = AsyncProxyFactory()
        time.sleep(10)
        self.assertEqual(proxy.get_uptime(), '0 days, 00:00:10')