import re
import unicodedata

nonalpha = re.compile("[^a-zA-Z]")
BLANK = "\N{LOWER ONE EIGHTH BLOCK}"


def preprocess(line, normalize, lowercase, add_blanks, order):
    if normalize:
        line = nonalpha.sub("", unicodedata.normalize("NFKD", line))

    if lowercase:  # check for bugs, lower was inside nonalpha.sub
        line = line.lower()

    if add_blanks:
        line = BLANK * (order - 1) + line + BLANK

    return line
