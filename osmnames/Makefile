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

all: brno.names.txt
.PHONY: all

clean:
	rm -f brno.names.txt
	rm -f brno.addrstreet.txt
	rm -f brno.waystreet.txt
	rm -f brno.names.xml
	rm -f brno.poly
	rm -f brno.boundary.xml
	rm -f jihomoravsky.osm.pbf
	rm -rf __pycache__
.PHONY: clean

jihomoravsky.osm.pbf:
	curl -- 'https://download.openstreetmap.fr/extracts/europe/czech_republic/jihomoravsky.osm.pbf' > jihomoravsky.osm.pbf

brno.boundary.xml: jihomoravsky.osm.pbf
	osmosis \
	  --read-pbf jihomoravsky.osm.pbf \
	  --tag-filter accept-relations "name=Brno" \
	  --tag-filter accept-relations "boundary=administrative" \
	  --write-xml - | \
	osmosis \
	  --read-xml - \
	  --used-way \
	  --used-node \
	  --write-xml brno.boundary.xml

brno.poly: brno.boundary.xml
	./admin_polygon brno.boundary.xml > brno.poly

brno.names.xml: jihomoravsky.osm.pbf brno.poly
	osmosis \
	  --read-pbf jihomoravsky.osm.pbf \
	  --bounding-polygon file=brno.poly \
	  --tag-filter accept-ways "name=*" \
	  --tag-filter accept-nodes "addr:street=*" \
	  --tag-filter reject-relations \
	  --write-xml brno.names.xml

brno.addrstreet.txt: brno.names.xml
	./get_addrstreet brno.names.xml > brno.addrstreet.txt

brno.waystreet.txt: brno.names.xml
	./get_waystreet brno.names.xml > brno.waystreet.txt

brno.names.txt: brno.addrstreet.txt brno.waystreet.txt
	cat brno.addrstreet.txt brno.waystreet.txt | LC_ALL=C sort | uniq > brno.names.txt
