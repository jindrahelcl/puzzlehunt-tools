import logging
import math

from collections import Counter
from warnings import warn


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)
LOG_EVERY=10000


def update_counts(counts, tokens, order):
    for n in range(order):
        for i in range(len(tokens) - n):
            ngram = tokens[i:i + n + 1]
            counts[n][ngram] += 1


def extract_counts(tokens, order):
    # return counts of different n-grams in the array
    counts = [Counter() for _ in range(order)]

    for n in range(order):
        for i in range(len(tokens) - n):
            ngram = tokens[i:i + n + 1]
            counts[n][ngram] += 1

    return counts


def total(counter):
    return sum(counter.values())


class SmoothedNGramModel:

    def __init__(self, order):
        self.order = order

        self.trained = False
        self.counts = None
        self.totals = None
        self.vocab_size = None

        self.heldout_counts = None
        self.heldout_totals = None

        self.lambdas = [1 / order for _ in range(order)]

    def single_prob(self, ngram):
        if len(ngram) > self.order:
            raise ValueError(f"'{ngram}' longer than {self.order}")

        # uniform probability: p(w) = 1 / vocabulary_size
        if not ngram:
            return 1 / self.vocab_size

        # unigram probability: p(w) = c(w) / data_size
        if len(ngram) == 1:
            return self.counts[0][ngram] / self.totals[0]

        # n-gram probability: p(w|h) = c(h,w) / c(h)
        ngram_count = self.counts[len(ngram) - 1][ngram]
        history_count = self.counts[len(ngram) - 2][ngram[:-1]]

        # for OOV history, this would be 0 / 0.
        # in +1 smoothing, we pretend we saw everything +1 times, i.e.
        # we saw the n-gram once and the (n-1)-gram vocabulary_size times.
        if ngram_count == 0 and history_count == 0:
            return 1 / self.vocab_size

        if ngram_count == 0:
            return 0

        return ngram_count / history_count

    def interpolated_prob(self, ngram):
        if len(ngram) != self.order:
            raise ValueError(f"ngram '{ngram}' is not an {self.order}-gram")

        single_probs_rev = reversed(
            [self.single_prob(ngram[n:]) for n in range(self.order)])

        interpolated_prob = 0.0
        for prob, weight in zip(single_probs_rev, self.lambdas):
            interpolated_prob += weight * prob

        return interpolated_prob

    def heldout_xent(self):
        xent = 0.0
        for ngram, freq in self.heldout_counts[self.order - 1].items():
            xent += freq * math.log(self.interpolated_prob(ngram))

        return - xent / total(self.heldout_counts[self.order - 1])

    def _load_data(self, data, preprocess=None):
        counts = [Counter() for _ in range(self.order)]

        for i, line in enumerate(data):
            if preprocess is not None:
                line = preprocess(line)

            update_counts(counts, line, self.order)

            if i > 0 and i % LOG_EVERY == 0:
                logger.info("%d lines loaded", i)

        return counts

    def train(self, train_data, preprocess=None):
        if self.trained:
            warn("Model already trained, overwriting", RuntimeWarning)

        self.counts = self._load_data(train_data, preprocess)
        self.totals = [total(self.counts[n]) for n in range(self.order)]
        self.vocab_size = len(self.counts[0])

    def heldout(self, heldout_data, preprocess=None):
        self.heldout_counts = self._load_data(heldout_data, preprocess)
        self.heldout_totals = [
            total(self.heldout_counts[n]) for n in range(self.order)]

    def lambda_expectation(self):
        lambda_counts = [0 for _ in range(self.order)]
        for ngram, freq in self.heldout_counts[self.order - 1].items():
            prob = self.interpolated_prob(ngram)

            for n in range(self.order):
                single_prob = self.single_prob(ngram[self.order - n - 1:])
                lambda_counts[n] += freq * self.lambdas[n] * single_prob / prob

        return lambda_counts

    def lambda_update(self, lambda_counts):
        self.lambdas = [l / sum(lambda_counts) for l in lambda_counts]

    def smooth(self, valid_every=10, epsilon=1.0e-4):

        prev_lambdas = [0] * self.order
        iteration = 0

        dist = lambda x, y: sum(abs(xi - yi) for xi, yi in zip(x, y))

        while dist(self.lambdas, prev_lambdas) > epsilon:
            iteration += 1

            lambda_counts = self.lambda_expectation()
            prev_lambdas = self.lambdas

            self.lambda_update(lambda_counts)

            if iteration % valid_every == 0:
                current_xent = self.heldout_xent()

                logger.info("Iteration %d, heldout cross-entropy: %.6f",
                            iteration, current_xent)
                logger.info("Lambdas: %s", ", ".join(map(str, self.lambdas)))

        logger.info("Finished after %d iterations.", iteration)
