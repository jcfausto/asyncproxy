#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#


def constant(c):
    """
    Since python doesn't have a constant type like other languages,
    this property type tries to simulate that by not allowing a property annoted to be written.
    """

    def cset(self, value):
        raise TypeError

    def cget(self):
        return c()

    return property(cget, cset)


class BytesTransferedOutputFormat(object):
    """
    This class provides all allowed output formats and convertion factors for the bytes_transferred info.
    """

    @constant
    def BYTES():
        return "bytes"

    @constant
    def KBYTES():
        return "kilobytes"

    @constant
    def MBYTES():
        return "megabytes"

    def kbytes_factor(self):
        return float(1 << 10)

    def mbytes_factor(self):
        return float(1 << 20)

"""
 Global to count bytes transferred
 Since Twisted is single threaded I won't worry about
 Synchronization here.
"""
bytes_transferred = 0


def update_usage(bytes_transferred):
    """
        Updates the accounting for proxy usage (bytes transferred)
        :param bytes_transferred: Some amount of bytes expressed as an int value
        :return: None
        """
    bytes_transferred += bytes_transferred


def get_bytes_transferred(output_format):
    """
        :param output_format: indicates the desired output format: B, KB or MB.
        :return: The amount of bytes transferred through the proxy in the indicated format.
        """

    formatter = BytesTransferedOutputFormat()

    if output_format == formatter.BYTES:
        return bytes_transferred
    elif output_format == formatter.KBYTES:
        return bytes_transferred / formatter.kbytes_factor()
    elif output_format == formatter.MBYTES:
        return bytes_transferred / formatter.mbytes_factor()
    else:
        return bytes_transferred
