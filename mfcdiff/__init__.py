# The MIT License (MIT)
# 
# Copyright (c) 2014 Josef Gajdusek
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
from termcolor import colored
from itertools import zip_longest
from pydoc import pager

class Block(list):

    def __init__(self, data, offset, trailer):
        self.extend(data)
        self._trailer = trailer
        self._offset = offset

    def is_trailer(self):
        return self._trailer

    def offset(self):
        return self._offset

class Card(list):

    def __init__(self, data):
        self._raw = list(data)

    def sectors(self):
        return self

    def raw(self):
        return self._raw

class Sector(list):

    def __init__(self, data, offset):
        self._offset = offset

    def offset(self):
        return self._offset

    def blocks(self):
        return self

class UltralightSector(Sector):

    def __init__(self, data, offset):
        super(UltralightSector, self).__init__(data, offset)
        for x in range(0, len(data), 4):
            self.append(Block(data[x:x + 4], offset + x, False))

class UltralightCard(Card):

    def __init__(self, data):
        super(UltralightCard, self).__init__(data)
        self.append(UltralightSector(data[0:4 * 4], 0))
        self.append(UltralightSector(data[4 * 4:], 4 * 4))

class ClassicSector(Sector):

    def __init__(self, data, offset, mad=None):
        super(ClassicSector, self).__init__(data, offset)
        self._mad = mad
        old = 0
        for i in range(16, len(data) + 1, 16):
            self.append(Block(data[old:i], offset + old,
                ClassicSector.is_trailer(offset + old)))
            old = i

    def mad(self):
        return self._mad

    @staticmethod
    def is_trailer(i):
        i /= 16
        if i <= 0x7f:
            return i % 4 == 3
        else:
            return i % 16 == 15

class ClassicCard(Card):

    def __init__(self, data):
        super(ClassicCard, self).__init__(data)
        old = 0
        mads = ClassicCard.get_mad_descriptors(data)
        for i in list(range(64, 32 * 64 + 1, 64)) + \
                list(range(2048 + 256, 4096 + 1, 256)):
            if i >= len(data):
                break
            self.append(ClassicSector(data[old:i], old, mad=mads[len(self)]))
            old = i

    @staticmethod
    def get_mad_descriptors(data):
        descs = []
        for x in [None] + list(range(0x12, 0x30, 2)) + \
                [None] + list(range(0x402, 0x430, 2)):
            if x != None and x >= len(data):
                break
            descs.append(
                    None if x == None else (data[x + 1] << 8 | data[x]))
        return descs

class Differ():

    def __init__(self, asc=False, space=True, mad=False):
        self._asc = asc
        self._space = space
        self._mad = mad

    def diff_blocks(self, blocks):
        ret = ""
        strings = [""] * len(blocks)
        for bs in zip_longest(*blocks):
            attrs = []
            color = None
            if blocks[0].is_trailer():
                color = "grey"
                attrs = ["bold"]
            if any([x != bs[0] for x in bs]):
                color = "green"
            for i, b in enumerate(bs):
                if self._asc:
                    if b == None:
                        s = " "
                    elif b in range(32, 127):
                        s = chr(b)
                    else:
                        s = "."
                else:
                    if b == None:
                        s = "  "
                    else:
                        s = "%02x" % b
                if self._space:
                    s += " "
                strings[i] += \
                    colored(s, color, attrs=attrs)

        return (("%03x | " if self._space else "%03x ") % (blocks[0].offset() / len(blocks[0]))) + \
                ("| " if self._space else " ").join(strings) + "\n"

    def diff_sectors(self, sectors):
        ret = ""
        if self._mad:
            madid = sectors[0].mad()
            if madid:
                madstring = "> %04x" % madid
            else:
                madstring = "> MAD"
            ret += colored(madstring, "yellow") + "\n"
        for blocks in zip_longest(*sectors):
            ret += self.diff_blocks(blocks)
        return ret

    def diff(self, cards):
        ret = ""
        for sectors in zip(*cards):
            ret += self.diff_sectors(sectors) + "\n"
        return ret
