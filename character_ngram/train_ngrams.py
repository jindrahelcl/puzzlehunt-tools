#!/usr/bin/env python3

import argparse
import logging
import re
import sys
import unicodedata

from ngram_model import SmoothedNGramModel

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

nonalpha = re.compile("[^a-zA-Z]")
BLANK = "\N{LOWER ONE EIGHTH BLOCK}"


def normalize(line):
    return nonalpha.sub("", unicodedata.normalize("NFKD", line))


def preprocess(line, args):
    if args.normalize:
        line = normalize(line)

    if args.lowercase: # check for bugs, lower was inside nonalpha.sub
        line = line.lower()

    if args.add_blanks:
        line = BLANK * (args.order - 1) + line + BLANK

    return line


def main(args):
    logger.info("Hello! This is %s", sys.argv[0])

    model = SmoothedNGramModel(args.order)
    model.train(args.input, preprocess=lambda x: preprocess(x, args))

    logger.info("Train data loaded, n-gram stats:")
    for n in range(model.order):
        logger.info("%d-grams: %d", n + 1, len(model.counts[n]))

    logger.info("Loading heldout set.")
    model.heldout(args.heldout, preprocess=lambda x: preprocess(x, args))

    logger.info("Heldout data loaded, n-gram stats:")
    for n in range(model.order):
        logger.info("%d-grams: %d", n + 1, len(model.heldout_counts[n]))

    logger.info("Calculating OOV rates on heldout set:")
    for n in range(model.order):
        oov = 0
        for ngram in model.counts[n].keys():
            if model.heldout_counts[n][ngram] == 0:
                oov += 1

        all_unique = len(model.heldout_counts[n])

        logger.info("OOV %d-grams: %d out of %d, that's %.1f percent", n + 1,
                    oov, all_unique, oov / all_unique * 100)

    current_xent = model.heldout_xent()
    logger.info("Initial heldout set cross-entropy: %.4f", current_xent)
    logger.info("Commencing Jelinek-Mercer smoothing parameter estimation...")

    model.smooth()

    logger.info("For lambdas:")
    for n in range(model.order):
        logger.info("%d: %.4f", n + 1, model.lambdas[n])

    logger.info("Saving model to %s", args.output)
    model.save(args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # pylint: disable=line-too-long
    parser.add_argument("input", nargs="?", metavar="INPUT_TRAIN", help="Input file. Plaintext. Default stdin.", default=sys.stdin, type=argparse.FileType("r"))
    parser.add_argument("output", nargs="?", metavar="MODEL_FILE", help="Model file", type=str)
    parser.add_argument("heldout", nargs="?", metavar="INPUT_HELDOUT", help="Heldout data. Plaintext.", type=argparse.FileType("r"))

    parser.add_argument("-n", "--order", help="Order of the language model. Default 4", default=4, type=int)
    parser.add_argument("--normalize", help="Normalize unicode to ascii", default=True, type=bool)
    parser.add_argument("--lowercase", help="Lowercase training data", default=True, type=bool)
    parser.add_argument("--add-blanks", help="Circumfix the lines with blank characters", default=True, type=bool)
    parser.add_argument("--epsilon", help="Convergence criterion. Small number.", default=1.0e-4, type=float)
    parser.add_argument("--valid-every", help="Number of iterations between validations.", default=10, type=int)

    p_args = parser.parse_args(sys.argv[1:])
    main(p_args)
