import gzip
import json
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

    def sort(self, lines):
        return sorted(lines, key=lambda line: self.loss(line))

    def best(self, limit, lines):
        yield "Not implemented. :-p"
        # TODO: implement an efficient best n algorithm
