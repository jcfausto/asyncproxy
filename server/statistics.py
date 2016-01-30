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


class _BytesTransferedOutputFormat(object):
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
