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
