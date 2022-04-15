import gzip
import json

class Jmc(object):
    def __init__(self, descriptor):
        self.order = descriptor["order"]
        self.vocab_size = descriptor["vocab_size"]
        self.lambdas = descriptor["lambdas"]
        self.counts = descriptor["counts"]
        self.totals = descriptor["totals"]

    @classmethod
    def load(cls, fp):
        with gzip.open(fp, "rt", encoding="utf-8") as zipfile:
            return cls(json.load(zipfile))
