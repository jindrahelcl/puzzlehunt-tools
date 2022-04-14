import gzip
import json

class Jmc(object):
    def __init__(self, descriptor):
        self.order = descriptor["order"]
        self.vocab_size = descriptor["vocab_size"]
        self.lambdas = descriptor["lambdas"]
        self.counts = descriptor["counts"]
        self.totals = descriptor["totals"]

    @staticmethod
    def load(fp):
        with gzip.open(fp, "rt", encoding="utf-8") as zipfile:
            return Jmc(json.load(zipfile))
