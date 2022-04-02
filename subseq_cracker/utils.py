#!/usr/bin/env python3

import itertools

def gen_perms(seq):
    return itertools.permutations(seq)

def is_subseq(s, l):
    if len(s) > len(l):
        return False

    if len(s) == len(l):
        return s==l

    i = 0
    for j, ch in enumerate(l):
        if i < len(s) and ch == s[i]:
            i += 1
        else:
            i = 0

        if i == len(s):
            return True

        # not enough characters left
        if (len(l)-j-1) < (len(s)-i-1):
            return False

    return False

def is_subseq_discont(s, l):
    if len(s) > len(l):
        return False

    if len(s) == len(l):
        return s==l

    i = 0
    for ch in l:
        if i < len(s) and ch == s[i]:
            i += 1
    return i == len(s)