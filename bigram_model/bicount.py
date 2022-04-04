#!/usr/bin/env python3

##
# Copyright (C) 2022 Tomas "trosos" Tintera
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

import marshal
import logging
import sys
from collections import Counter
from math import log
from string import ascii_lowercase
from itertools import product

from bisort import normalize

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)
LOG_EVERY=1000000

if len(sys.argv) != 1:
    sys.exit(f"Usage: {sys.argv[0]} < source.txt > model.bin")

total = 0
counts = Counter()

logger.info("Loading data, will report every %d lines", LOG_EVERY)
for i, line in enumerate(sys.stdin):
    text = normalize(line)
    if text:
        total += len(text) - 1
        counts += Counter("".join(bigram) for bigram in zip(text, text[1:]))

    if i > 0 and i % LOG_EVERY == 0:
        logger.info("%d sentences loaded", i)


logger.info("Data loading done. Read %d characters", total)
statistics = {bigram: log(total/count) for bigram, count in counts.items()}
inf = max(count for count in statistics.values())
defaults = {"".join(bigram): inf for bigram in product(*2*[ascii_lowercase])}
complete_statistics = {**defaults, **statistics}

sys.stdout.buffer.write(marshal.dumps(complete_statistics))
