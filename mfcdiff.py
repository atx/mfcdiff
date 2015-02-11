#! /usr/bin/env python3

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
from functools import reduce
from itertools import zip_longest
from pydoc import pager

parser = argparse.ArgumentParser(
    prog="mfcdiff",
    usage="mfcdiff <first.mfd> <second.mfd>"
)
parser.add_argument(
    "-p",
    "--pager",
    action="store_true",
    help="Use pager to display the output"
)
parser.add_argument(
    "-a",
    "--ascii",
    action="store_true",
    help="Display ASCII instead of hex"
)
parser.add_argument(
    "-s",
    "--no-space",
    action="store_true",
    help="Do not put spaces between bytes"
)
parser.add_argument(
    "-m",
    "--mad",
    action="store_true",
    help="Dump the MAD descriptors"
)
parser.add_argument(
    nargs=argparse.REMAINDER,
    dest="dumps",
    help="List of .mfd files"
)
parser.add_argument(
    "-c",
    "--card",
    nargs="?",
    default="4k",
    choices=["1k", "4k"]
)


def get_block_number(i, mode):
    return int(i / 16)

def block_to_sec(i, mode):
    if mode == "1k":
        return int(i / 4)
    elif mode == "4k":
        if i <= 0x7f:
            return int(i / 4)
        else:
            return int((i - 0x80) / 16) + 32

def is_key_block(i, mode):
    if mode == "1k":
        return i % 4 == 3
    elif mode == "4k":
        if i <= 0x7f:
            return i % 4 == 3
        else:
            return i % 16 == 15

def get_mad_descriptors(data, mode):
    version = 1 if mode == "1k" else 2
    descs = []
    for x in [None] + list(range(0x12, 0x30, 2)) + \
            [None] + list(range(0x402, 0x430, 2)):
        descs.append(colored("> MAD" if x == None
                else ("> %02x%02x" % (data[x + 1], data[x])), "yellow"))
    return descs

def get_diff(binaries, mode, asc=False, space=True, mad=False):
    ret = ""
    strings = [""] * len(binaries)
    nblk = 0
    nsec = 0
    if mad:
        mads = get_mad_descriptors(binaries[0], mode)
    for i, data in enumerate(zip_longest(*binaries)):
        color = None
        attrs = None
        if is_key_block(nblk, mode):
            color = "grey"
            attrs = ["bold"]
        if any([x != data[0] for x in data]):
            color = "green"

        for j, d in enumerate(data):
            if asc:
                if d == None:
                    s = " "
                elif d >= 32 and d <= 126:
                    s = chr(d)
                else:
                    s = "."
            else:
                if d == None:
                    s = "  "
                else:
                    s = "%02x" % d
            if space:
                s += " "
            strings[j] += colored(s, color, attrs=attrs)

        if nblk != get_block_number(i + 1, mode):
            nblk = get_block_number(i + 1, mode)

            strings = [s.strip() for s in strings]
            ret += "%03x | " % (nblk - 1) + \
                reduce(lambda i, v: i + ("| " if space else " ") + v, strings) + "\n"

            strings = [""] * len(binaries)
        if nsec != block_to_sec(nblk, mode) or i == 0:
            nsec = block_to_sec(nblk, mode)
            if i != 0:
               ret += "\n"
            if mad and nsec < len(mads):
                ret += mads[nsec] + "\n"

    return ret



args = parser.parse_args()

binaries = []
for fname in args.dumps:
    with open(fname, "rb") as f:
        binaries.append(f.read())

diff = get_diff(binaries, args.card, asc=args.ascii,
        space=(not args.no_space), mad=args.mad)
if args.pager:
    pager(diff)
else:
    print(diff)
