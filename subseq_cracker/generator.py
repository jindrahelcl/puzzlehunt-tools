#!/usr/bin/env python3

import sys
from utils import *

def get_generator(classname):
    try:
        return getattr(sys.modules[__name__], classname)
    except AttributeError:
        logger.error(f"Unknown generator: '{classname}'.")
        return None

class Generator:
    def __iter__(self):
        pass

class Tmou(Generator):
    def __init__(self):
        pass
        
    def __iter__(self):
        pass


class SimpleGenerator(Generator):
    # do not change, used for examining a single string
    def __init__(self, letters):
        self.letters = letters

    def __iter__(self):
        yield self.letters


class GenPotrati(Generator):
    def __init__(self):
        self.a = ["návěstidlo", "drátytelegrafníhovedení", "potůček", "přístupovácesta", "cestička" , "vozidlo", "vextrovna"]
        self.b = [(4,9), (6,6), (5,1), (7,11), (6,12), (7,3), (3,2), (4,8), (5,7), (7,13), (4,10), (5,14), (6,4), (8,5)]

    def __iter__(self):
        for perm in gen_perms(self.a):
            seq = []
            for l, word in enumerate(perm):
                for i in range(2):
                    coord = self.b[l*2+i]     
                    char_idx = coord[0]-1

                    if len(word) <= char_idx:
                        continue

                    seq.append((word[char_idx], coord[1]))

            if len(seq) != len(self.b):
                continue

            seq.sort(key=lambda x: x[1])
            seq = [x[0] for x in seq]
            yield "".join(seq)
