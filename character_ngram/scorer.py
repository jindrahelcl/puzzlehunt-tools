#!/usr/bin/env python3

import argparse
import logging
import sys

from ngram_model import SmoothedNGramModel
from string_util import preprocess

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def main(args):
    logger.info("Hello! This is %s", sys.argv[0])

    model = SmoothedNGramModel.load(args.model)

    logger.info(
        "%d-gram model file %s loaded, scoring", model.order, args.model)

    preprocess_fn = lambda x: preprocess(x, args.normalize, args.lowercase,
                                         args.add_blanks, model.order)

    for i, line in enumerate(args.input):
        score = model.score(preprocess_fn(line))
        print(score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "model", metavar="MODEL_FILE", type=str, help="Model file")
    parser.add_argument(
        "input", nargs="?", metavar="INPUT", default=sys.stdin,
        help="Input file. Plaintext. Default stdin.",
        type=argparse.FileType("r"))
    parser.add_argument(
        "output", nargs="?", metavar="OUTPUT", default=sys.stdout,
        type=argparse.FileType("w"))
    parser.add_argument(
        "--normalize", default=True, type=bool,
        help="Normalize unicode to ascii")
    parser.add_argument(
        "--lowercase", default=True, type=bool,
        help="Lowercase training data")
    parser.add_argument(
        "--add-blanks", default=True, type=bool,
        help="Circumfix the lines with blank characters")

    p_args = parser.parse_args(sys.argv[1:])
    main(p_args)
