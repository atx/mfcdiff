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
            return int(i / 16)

def is_key_block(i, mode):
    if mode == "1k":
        return i % 4 == 3
    elif mode == "4k":
        if i <= 0x7f:
            return i % 4 == 3
        else:
            return i % 16 == 15

def get_diff(binaries, mode, asc=False, space=True):
    ret = ""
    strings = [""] * len(binaries)
    nblk = 0
    nsec = 0
    for i, data in enumerate(zip(*binaries)):
        color = None
        attrs = None
        if is_key_block(nblk, mode):
            color = "grey"
            attrs = ["bold"]
        if any([x != data[0] for x in data]):
            color = "green"

        for j, d in enumerate(data):
            if asc:
                if d >= 32 and d <= 126:
                    s = chr(d)
                else:
                    s = "."
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
            if nsec != block_to_sec(nblk, mode):
                nsec = block_to_sec(nblk, mode)
                ret += "\n"

            strings = [""] * len(binaries)

    return ret



args = parser.parse_args()

binaries = []
for fname in args.dumps:
    with open(fname, "rb") as f:
        binaries.append(f.read())

diff = get_diff(binaries, args.card, asc=args.ascii, space=(not args.no_space))
if args.pager:
    pager(diff)
else:
    print(diff)

