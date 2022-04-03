##
# Copyright (C) 2022 Tomas "trosos" Tintera
#
# Permission to use, copy, modify, and/or distribute this
# software for any purpose with or without fee is hereby
# granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS
# ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH
# THE USE OR PERFORMANCE OF THIS SOFTWARE.
##

def normalize(text):
    return (text
        .replace("\u00a0", " ")    # NBSP
        .replace("\u200b", "")     # ZWSP
        .replace("\u2013", "-")    # NDASH
        .replace("\u2014", "-")    # MDASH
        .replace("\u2019", "'")    # Right Single Quotation Mark
        .replace("\u2160", "I")    # Roman Numeral One
        .replace("\u2161", "II")   # Roman Numeral Two
        .replace("\u2162", "III")  # Roman Numeral Three
        .replace("\u2163", "IV")   # Roman Numeral Four
        .replace("\u2164", "V")    # Roman Numeral Five
        .replace("\u2165", "VI")   # Roman Numeral Six
        .replace("\u2166", "VII")  # Roman Numeral Seven
        .replace("\u2167", "VIII") # Roman Numeral Eight
        .replace("\u2168", "IX")   # Roman Numeral Nine
        .replace("\u2169", "X")    # Roman Numeral Ten
        .replace("\u21d4", "<=>")  # Left Right Double Arrow
    )
