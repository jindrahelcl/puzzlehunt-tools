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

ENDPOINT := https://download.openstreetmap.fr/extracts/europe/czech_republic/
CITIES := praha brno
praha_PBF := praha.osm.pbf
praha_NAME := Praha
brno_PBF := jihomoravsky.osm.pbf
brno_NAME := Brno


all: $(CITIES:=.names.txt)
.PHONY: all

clean:
	rm -f *.names.txt
	rm -f *.addrstreet.txt
	rm -f *.waystreet.txt
	rm -f *.names.xml
	rm -f *.poly
	rm -f *.boundary.xml
	rm -f *.osm.pbf
	rm -rf __pycache__
.PHONY: clean

$(foreach city,$(CITIES),$($(city)_PBF)):
	curl -- $(ENDPOINT)$@ > $@

.SECONDEXPANSION:

$(CITIES:=.boundary.xml): %.boundary.xml: $${$$*_PBF}
	osmosis \
	  --read-pbf $< \
	  --tag-filter accept-relations "name=$($*_NAME)" \
	  --tag-filter accept-relations "type=boundary" \
	  --tag-filter accept-relations "boundary=administrative" \
	  --tag-filter accept-relations "admin_level=8" \
	  --write-xml - | \
	osmosis \
	  --read-xml - \
	  --used-way \
	  --used-node \
	  --write-xml $@

$(CITIES:=.poly): %.poly: %.boundary.xml
	./admin_polygon $< > $@

$(CITIES:=.names.xml): %.names.xml: $${$$*_PBF} %.poly
	osmosis \
	  --read-pbf $($*_PBF) \
	  --bounding-polygon file=$*.poly \
	  --tag-filter accept-ways "name=*" \
	  --tag-filter accept-nodes "addr:street=*" \
	  --tag-filter reject-relations \
	  --write-xml $@

$(CITIES:=.addrstreet.txt): %.addrstreet.txt: %.names.xml
	./get_addrstreet $< > $@

$(CITIES:=.waystreet.txt): %.waystreet.txt: %.names.xml
	./get_waystreet $< > $@

$(CITIES:=.names.txt): %.names.txt: %.addrstreet.txt %.waystreet.txt
	cat $+ | LC_ALL=C sort | uniq > $@
