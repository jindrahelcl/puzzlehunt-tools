#!/usr/bin/env python3

from utils import *
import unittest


class TestSubseqDiscont(unittest.TestCase):
    def test_is_subseq(self):
        self.assertTrue(is_subseq_discont([1, 3, 5], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq_discont([1], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq_discont([5], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq_discont([1, 5], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq_discont([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq_discont([], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq_discont([], [1]))
        self.assertTrue(is_subseq_discont([1], [1]))
        self.assertTrue(is_subseq_discont([], []))

    def test_is_not_subseq(self):
        self.assertFalse(is_subseq([1, 2, 3, 4, 5, 5], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq_discont([1, 5, 4], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq_discont([5, 1], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq_discont([6], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq_discont([1], []))


class TestSubseq(unittest.TestCase):
    def test_is_subseq(self):
        self.assertTrue(is_subseq([1], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq([5], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq([1, 2], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq([], [1, 2, 3, 4, 5]))
        self.assertTrue(is_subseq([], [1]))
        self.assertTrue(is_subseq([1], [1]))
        self.assertTrue(is_subseq([], []))

    def test_is_not_subseq(self):
        self.assertFalse(is_subseq([1, 5], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq([1, 3, 5], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq([1, 2, 3, 4, 5, 5], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq([1, 5, 4], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq([5, 1], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq([6], [1, 2, 3, 4, 5]))
        self.assertFalse(is_subseq([1], []))

if __name__ == '__main__':
    unittest.main()