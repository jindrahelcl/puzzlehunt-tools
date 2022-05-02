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

import gzip
import heapq
import json
import math
import re
import unicodedata


class Jmc(object):
    _nonalpha = re.compile("[^a-z]")

    def __init__(self, stats):
        self.order = len(stats)
        self.stats = stats

    def get_descriptor(self):
        return {"stats": self.stats}

    def dump(self, fp):
        with gzip.open(fp, "wt", encoding="ascii") as zipfile:
            json.dump(self.get_descriptor(), zipfile, indent=4, sort_keys=True)
            zipfile.write("\n")

    @classmethod
    def load(cls, fp):
        with gzip.open(fp, "rt", encoding="utf-8") as zipfile:
            return cls(**json.load(zipfile))

    def decorate(self, line):
        return (self.order - 1)*"\n" + line + "\n"

    def undecorate(self, line):
        return line[self.order - 1:-1]

    @staticmethod
    def latin(line):
        return Jmc._nonalpha.sub(
            "", unicodedata.normalize("NFKD", line).lower()
        )

    @staticmethod
    def alpha(line):
        import unidecode
        return Jmc._nonalpha.sub("", unidecode.unidecode(line).lower())

    def single_loss(self, ngram, prev_order):
        order = self.order
        skip = max(0, order - prev_order - 1)
        losses = (
            self.stats[k].get(ngram[k + skip:])
            for k in range(order)
        )
        return next(
            (loss, -k) for k, loss in enumerate(losses, skip - order)
            if loss is not None
        )

    def losses(self, line):
        ngrams = (
            line[k:k + self.order]
            for k in range(len(line) - self.order + 1)
        )

        prev_order = self.order
        for ngram in ngrams:
            loss, prev_order = self.single_loss(ngram, prev_order)
            yield loss

    def loss(self, line):
        return sum(self.losses(line))/(len(line) + 1 - self.order)
        # TODO: peek at next line and determine x=len(os.path.commonprefix);
        # cache prev_order and sum of losses corresponding to numbers up to x;
        # and use it next time to speed up calculation

    def iloss(self, line, top):
        result = 0
        for loss in self.losses(line):
            result += loss
        return result/(len(line) + 1 - self.order)

    def sort(self, lines):
        return sorted(lines, key=lambda line: self.loss(line))
        # TODO: implement external sort, to avoid RAM depletion
        # TODO: before scoring, put common prefixes together and make use of it

    @staticmethod
    def nlargest(n, iterable, key):
        result = [(key(elem), i, elem)
                  for i, elem in zip(range(0, -n, -1), iterable)]
        if not result:
            return result
        heapq.heapify(result)
        top = result[0][0]
        order = -n
        heapreplace = heapq.heapreplace
        for elem in iterable:
            k = key(elem, top)
            if top < k:
                heapreplace(result, (k, order, elem))
                top = result[0][0]
                order -= 1
        result.sort(reverse=True)
        return [elem for (k, order, elem) in result]

    def best(self, limit, lines):
        return self.nlargest(
            limit, lines,
            key=lambda line, top=math.inf: -self.iloss(line, top),
        )
        # TODO: before scoring, put common prefixes together and make use of it
