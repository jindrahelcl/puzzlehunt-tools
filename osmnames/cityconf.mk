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

# Here you can define custom cities to build.

CITIES := praha brno bratislava

ENDPOINT := https://download.openstreetmap.fr/extracts/

praha_URL := $(ENDPOINT)europe/czech_republic/praha.osm.pbf
praha_LEVEL := 8
praha_NAME := Praha

brno_URL := $(ENDPOINT)europe/czech_republic/jihomoravsky.osm.pbf
brno_LEVEL := 8
brno_NAME := Brno

bratislava_URL := $(ENDPOINT)europe/slovakia/bratislavsky.osm.pbf
bratislava_LEVEL := 6
bratislava_NAME := Bratislava
