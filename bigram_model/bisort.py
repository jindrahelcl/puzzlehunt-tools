#!/usr/bin/env python3

##
# Copyright (C) 2022 Tomas Tintera
#
# Permission to use, copy, modify, and/or distribute this
# software for any purpose with or without fee is hereby
# granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS
# ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH
# THE USE OR PERFORMANCE OF THIS SOFTWARE.
##

from sys import stdin, argv, exit
import unicodedata
import re
import marshal

nonalpha = re.compile("[^a-zA-Z]")

def bigram_loss(bigram):
    return bigram_statistics[bigram]

def text_loss(text):
    return sum(bigram_loss("".join(bigram)) for bigram in zip(text, text[1:]))/(len(text)-1)

def sort_texts(texts):
    return sorted(texts, key=text_loss)

def normalize(text):
    return nonalpha.sub("", unicodedata.normalize("NFKD", text).lower())

if __name__ == "__main__":
    if len(argv) != 2:
        exit("Usage: {} model.bin < input.txt".format(argv[0]))
    with open(argv[1], "rb") as f:
        bigram_statistics = marshal.load(f)
    print("\n".join(sort_texts(normalize(text) for text in stdin.readlines())))
