#!/usr/bin/env python3

from itertools import permutations
interactive = False

words = ["vozidlo", "vechtrovna", "navestidlo", "dratytelegrafnihovedeni", "potucek", "pristupovacesta", "cesticka"]
letters = [5, 3, 7, 6, 8, 6, 5, 4, 4, 4, 7, 6, 7, 5]
on_left = [True, True, False, True, False, False, True, False, True, True, False, True, False, False]
fin = []
for p in permutations(words):
    a = [p[f] for f in [1,3,2,6,6,0,4,3,0,5,1,2,4,5]]
    taj = ""
    for i, left, w in zip(letters, on_left, a):
        if i > len(w):
            break
        if left:
            taj += w[i-1]
        else:
            taj += w[i-1]
    if len(taj) == 14:
        fin.append(taj)

k = 0
for bon in sorted(fin):
    print(bon)
    k += 1
    if k%15 == 0 and interactive:
        input(k)
