#!/usr/bin/env python3

import argparse
import logging
import math
import re
import sys
import unicodedata

from collections import Counter

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)
LOG_EVERY = 10000

nonalpha = re.compile("[^a-zA-Z]")
BLANK = "▁"

def total(counter):
    return sum(counter.values())

def normalize(line):
    return nonalpha.sub("", unicodedata.normalize("NFKD", line))


def extract_counts(line, order, added_blanks=True):
    # split the text into characters and return counts of different ngrams
    counts = [Counter() for _ in range(order)]

    for n in range(order):
        for i in range(len(line) - n):
            ngram = line[i:i + n + 1]
            counts[n][ngram] += 1

    # for i in range(len(line) - order + 1):
    #     ngram = line[i:i + order]
    #     for n in range(order):
    #         # counts[0] are unigram counts, etc.
    #         counts[n][ngram[:n + 1]] += 1
    #         counts[n][ngram[order - n - 1:]] += 1

    # logger.info("sentence %s", line)
    # logger.info("got counts %s", str(counts))

    return counts


def logsumexp(probs):
    maxprob = max(probs)
    return maxprob + math.log(sum(math.exp(p - maxprob) for p in probs))


def single_logprob(ngram, counts, vocab_size):
    order = len(counts)

    if len(ngram) > order:
        raise AssertionError(f"sorry '{ngram}' is longer than {order} chars")

    if not ngram:
        # return uniform probability
        return -math.log(vocab_size)

    if len(ngram) == 1:
        # unigram probability p(x) = c(x) / |T|
        data_size = total(counts[0])
        return math.log(counts[0][ngram]) - math.log(data_size)

    # n-gram probability: p(x|h) = c(h,x) / c(h)
    ngram_logcount = math.log(counts[len(ngram) - 1][ngram])
    history_logcount = math.log(counts[len(ngram) - 2][ngram[:-1]])
    return ngram_logcount - history_logcount


def single_prob(ngram, counts, vocab_size):
    order = len(counts)

    if len(ngram) > order:
        raise AssertionError(f"sorry '{ngram}' is longer than {order} chars")

    if not ngram:
        # return uniform probability
        return 1 / vocab_size

    if len(ngram) == 1:
        # unigram probability p(x) = c(x) / |T|
        data_size = total(counts[0])
        return counts[0][ngram] / data_size

    # n-gram probability: p(x|h) = c(h,x) / c(h)
    ngram_count = counts[len(ngram) - 1][ngram]
    history_count = counts[len(ngram) - 2][ngram[:-1]]

    if ngram_count == 0 and history_count == 0:
        return 1 / vocab_size

    if ngram_count == 0:
        return 0

    return ngram_count / history_count


def interpolated_prob(ngram, counts, vocab_size, lambdas):

    order = len(counts)
    if len(lambdas) != order:
        raise AssertionError(f"order {order} is not len lambdas {len(lambdas)}")

    if len(ngram) != order:
        raise AssertionError(f"ngram '{ngram}' is not of order {order}")

    single_probs = reversed([single_prob(ngram[n:], counts, vocab_size) for n in range(order)])

    interpolated_prob = 0.0
    for prob, weight in zip(single_probs, lambdas):
        interpolated_prob += weight * prob

    return interpolated_prob


def heldout_xent(counts, vocab_size, lambdas, heldout_counts):
    xent = 0.0
    for ngram, freq in heldout_counts.items():
        xent += freq * math.log(interpolated_prob(ngram, counts, vocab_size, lambdas))

    return - xent / total(heldout_counts)


def expectation(counts, vocab_size, lambdas, heldout_counts):
    # SUM FOR i in 1 .. heldout_size OF lambda_j p_j(w_i|h_i) / p'lambda
    order = len(counts)

    lambda_counts = [0 for _ in range(order)]
    for n in range(order):
        for ngram, freq in heldout_counts.items():
            lambda_counts[n] += freq * lambdas[n] * single_prob(ngram[order - n:], counts, vocab_size) / interpolated_prob(ngram, counts, vocab_size, lambdas)

    return lambda_counts


def normalize_lambdas(lambda_counts):
    return [l / sum(lambda_counts) for l in lambda_counts]


def preprocess(line, args):
    if args.normalize:
        line = normalize(line)

    if args.lowercase: # check for bugs, lower was inside nonalpha.sub
        line = line.lower()

    if args.add_blanks:
        line = BLANK * (args.order - 1) + line + BLANK

    return line


def main(args):
    logger.info("Hello! I am a useless log message telling you we have started!")

    counts = [Counter() for _ in range(args.order)]

    for i, line in enumerate(args.input):
        line = preprocess(line, args)

        new_counts = extract_counts(line, args.order)
        for n in range(args.order):
            counts[n] += new_counts[n]

        if i > 0 and i % LOG_EVERY == 0:
            logger.info("%d sentences loaded", i)

    totals = [total(counts[n]) for n in range(args.order)]
    vocab_size = len(counts[0])

    logger.info("Data loading done, here are the counts of unique n-grams:")
    for n in range(args.order):
        logger.info("%d-grams: %d", n + 1, len(counts[n]))

    logger.info("Loading heldout set.")
    heldout_counts = Counter()  # we are only counting highest-order ngrams
    for i, line in enumerate(args.heldout):
        line = preprocess(line, args)
        heldout_counts += extract_counts(line, args.order)[args.order - 1]

    logger.info("Heldout set loaded. Contains %d %dgrams", total(heldout_counts), args.order)
    #import ipdb;ipdb.set_trace()

    prev_lambdas = [0] * args.order
    lambdas = [1 / args.order] * args.order

    current_xent = heldout_xent(counts, vocab_size, lambdas, heldout_counts)
    logger.info("Initial heldout set cross-entropy: %.4f", current_xent)

    logger.info("Commencing Jelinek-Mercer smoothing parameter estimation...")

    iteration = 0

    while sum((c - p) ** 2 for c, p in zip(lambdas, prev_lambdas)) > args.epsilon:
        iteration += 1

        lambda_counts = expectation(counts, vocab_size, lambdas, heldout_counts)

        prev_lambdas = lambdas
        lambdas = normalize_lambdas(lambda_counts)

        if iteration % args.valid_every == 0:
            current_xent = heldout_xent(counts, vocab_size, lambdas, heldout_counts)

            logger.info("Iteration %d, heldout cross-entropy: %.4f", iteration, current_xent)
            logger.info("Lambdas: %s", ", ".join(map(str, lambdas)))


    logger.info(f"Finished after {iteration} iterations.")
    logger.info("For lambdas:")
    for n in range(args.order):
        logger.info("%d: %.4f", n + 1, lambdas[n])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", nargs="?", metavar="INPUT_TRAIN", help="Input file. Plaintext. Default stdin.", default=sys.stdin, type=argparse.FileType("r"))
    parser.add_argument("output", nargs="?", metavar="MODEL_FILE", help="Model file", default=sys.stdout, type=argparse.FileType("w"))
    parser.add_argument("heldout", nargs="?", metavar="INPUT_HELDOUT", help="Heldout data. Plaintext.", type=argparse.FileType("r"))

    parser.add_argument("-n", "--order", help="Order of the language model. Default 4", default=4, type=int)
    parser.add_argument("--normalize", help="Normalize unicode to ascii", default=True, type=bool)
    parser.add_argument("--lowercase", help="Lowercase training data", default=True, type=bool)
    parser.add_argument("--add-blanks", help="Circumfix the lines with blank characters", default=True, type=bool)
    parser.add_argument("--epsilon", help="Convergence criterion. Small number.", default=1.0e-4, type=float)
    parser.add_argument("--valid-every", help="Number of iterations between validations.", default=10, type=int)

    args = parser.parse_args(sys.argv[1:])
    main(args)
