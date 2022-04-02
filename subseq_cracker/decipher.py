#!/usr/bin/env python3

import os
import argparse
import logging
import pandas as pd
import itertools
import unidecode
import re
import random
import generator

from utils import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


class SubseqPOICracker:
    def __init__(self, input, permute=False, use_unicode=False, min_k_letters=5):
        self.use_unicode = use_unicode
        self.permute = permute
        self.min_k_letters = min_k_letters
        self.df = pd.read_csv(input, header=0)
        self.places_orig = list(self.df["name"])
        self.places = list(map(self.normalize, enumerate(self.places_orig[:])))
        self.places = list(filter(lambda x: len(x[1])>=self.min_k_letters, self.places))
        self.matches = set()

    def normalize(self, o):
        idx, s = o
        if self.use_unicode:
            s = re.sub(r'[^\w\d]+', '', s)
        else:
            s = unidecode.unidecode(s)
            s = re.sub(r'[^0-9a-zA-Z]+', '', s)

        s = s.lower()

        if self.permute:
            letset = list(sorted(s))
        else:
            letset = list(s)

        return idx, s, letset


    def examine(self, letset):
        subseq_fn = is_subseq_discont if self.permute else is_subseq

        for idx, place, place_letset in self.places:
            if subseq_fn(place_letset, letset) and place not in self.matches:
                logger.info("============================")
                logger.info(f"[MATCH] \"{self.places_orig[idx]}\" {place} {''.join(letset)}")
                logger.info("============================")

                self.matches.add(place)

    def crack(self, g):
        for i, example in enumerate(g):
            if type(example) is list:
                example = "".join(example)

            if not self.use_unicode:
                example = unidecode.unidecode(example)

            letset = list(example)
            if self.permute:
                letset.sort()

            self.examine(letset)

            if i % 1000 == 0:
                logger.info(f"Testing permutation #{i}: {example}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True,
        help="Input CSV with POIs.")
    parser.add_argument("-l", "--letters", type=str, default=None,
        help="A string of letters, a haystack in which a place should be found.")
    parser.add_argument("-k", "--min_k_letters", type=int, default=5,
        help="Use places with a least k letters.")
    parser.add_argument("-g", "--generator", type=str, default=None,
        help="A class name (case sensitive) of a generator of strings.")
    parser.add_argument("-u", "--unicode", action="store_true",
        help="Keep unicode characters. If omitted, places are converted to ASCII.")
    parser.add_argument("-p", "--permute",  action="store_true",
        help="All generated strings are considered unordered. Can be used for finding permutations.")

    args = parser.parse_args()
    logger.info(args)

    random.seed(42)

    c = SubseqPOICracker(
        input=args.input, 
        permute=args.permute, 
        use_unicode=args.unicode,
        min_k_letters=args.min_k_letters
    )
    if args.generator:
        g = generator.get_generator(args.generator)()
    elif args.letters:
        letters = list(args.letters)
        g = generator.get_generator("SimpleGenerator")(letters)

    c.crack(g)