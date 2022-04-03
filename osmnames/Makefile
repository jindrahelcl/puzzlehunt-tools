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

include cityconf.mk

all: $(CITIES:=.names.txt) $(CITIES:=.names.ascii.txt)
.PHONY: all

clean:
	rm -f $(CITIES:=.names.ascii.txt)
	rm -f $(CITIES:=.names.txt)
	rm -f $(CITIES:=.addrstreet.txt)
	rm -f $(CITIES:=.waystreet.txt)
	rm -f $(CITIES:=.names.xml)
	rm -f $(CITIES:=.poly)
	rm -f $(CITIES:=.boundary.xml)
	rm -f $(notdir $(foreach city,$(CITIES),$($(city)_URL)))
	rm -rf __pycache__
.PHONY: clean

$(foreach city,$(CITIES:=_URL),$(eval $(notdir $($(city))): URL := $($(city))))
$(notdir $(foreach city,$(CITIES),$($(city)_URL))):
	curl -- $(URL) > $@

.SECONDEXPANSION:

$(CITIES:=.boundary.xml): %.boundary.xml: $$(notdir $$($$*_URL))
	osmosis \
	  --read-pbf $< \
	  --tag-filter accept-relations "name=$($*_NAME)" \
	  --tag-filter accept-relations "type=boundary" \
	  --tag-filter accept-relations "boundary=administrative" \
	  --tag-filter accept-relations "admin_level=$($*_LEVEL)" \
	  --write-xml - | \
	osmosis \
	  --read-xml - \
	  --used-way \
	  --used-node \
	  --write-xml $@

$(CITIES:=.poly): %.poly: %.boundary.xml
	./admin_polygon $< > $@

$(CITIES:=.names.xml): %.names.xml: $$(notdir $$($$*_URL)) %.poly
	osmosis \
	  --read-pbf $(notdir $($*_URL)) \
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

$(CITIES:=.names.ascii.txt): %.names.ascii.txt: %.names.txt
	./normascii < $< | LC_ALL=C sort | uniq > $@
