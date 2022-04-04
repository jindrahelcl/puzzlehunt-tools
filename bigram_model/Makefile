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

include ../osmnames/cityconf.mk

all: $(CITIES:=.model)
.PHONY: all

clean:
	rm -f $(CITIES:=.model)
	rm -rf __pycache__
.PHONY: clean

$(CITIES:%=../osmnames/%.names.ascii.txt): ../osmnames/%:
	$(MAKE) -C ../osmnames $*

$(CITIES:=.model): %.model: ../osmnames/%.names.ascii.txt bicount.py bisort.py
	./bicount.py < $< > $@
