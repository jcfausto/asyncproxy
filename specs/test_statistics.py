#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#


from unittest import TestCase
from server.statistics import BytesTransferedOutputFormat


class TestStatistics(TestCase):

    def test_byte_constant_prints_bytes(self):
        """
        BYTES constant should have the value "bytes"
        """
        formatter = BytesTransferedOutputFormat()
        self.assertEqual(formatter.BYTES, 'bytes')

    def test_kbytes_constant_prints_kilobytes(self):
        """
        KBYTES constant should have the value "kilobytes"
        """
        formatter = BytesTransferedOutputFormat()
        self.assertEqual(formatter.KBYTES, 'kilobytes')

    def test_mbytes_constant_prints_megabytes(self):
        """
        MBYTES constant should have the value "megabytes"
        """
        formatter = BytesTransferedOutputFormat()
        self.assertEqual(formatter.MBYTES, 'megabytes')