# Subsequence Cracker :cyclone:
## Usage examples

### Find if there a permutation of a given string containing a place in Brno
```
./decipher.py  -i ../data/poi/brno.csv -l "xyzrdaoskhixyz" -p
```
Output:
```
[MATCH] "Hradisko" hradisko adhikorsxxyyzz
[MATCH] "Horská" horska adhikorsxxyyzz
[MATCH] "Oskar" oskar adhikorsxxyyzz
[MATCH] "Doširak" dosirak adhikorsxxyyzz
[MATCH] "Oříšky" orisky adhikorsxxyyzz
[MATCH] "YOSHI" yoshi adhikorsxxyyzz
```
### ...with at least 7 letters:
```
./decipher.py  -i ../data/poi/brno.csv -l "xyzrdaoskhixyz" -p -k 7
```
Output:
```
[MATCH] "Hradisko" hradisko adhikorsxxyyzz
[MATCH] "Doširak" dosirak adhikorsxxyyzz
```
### ...minding Unicode characters:
```
./decipher.py  -i ../data/poi/brno.csv -l "xyzrdaoskhixyz" -p -k 7 -u
```
Output:
```
[MATCH] "Hradisko" hradisko adhikorsxxyyzz
```

### Find if any string from a custom generator contains a place in Prague
Add a new class to `generator.py` and implement the `__iter__(self)` method. Get inspired by existing examples. The most straightforward case is to add a `for` loop and `yield` every generated example.

Remember the name of the class, e.g. `MyGenerator`.

Then run:
```
./decipher.py -i ../data/poi/praha.csv -g MyGenerator
```

You can use the same options as before (`-p` ignores the order of letters and can thus generate more matches).


### Find if a string contains any "common" puzzlehunt word
Use `../data/lexicon/common.csv` as an input.


### Extract POIs for an area

Make sure you have an OpenStreet Map `PBF` file (e.g. `czech-republic-latest.osm.pbf` from [here](https://download.geofabrik.de/europe/czech-republic.html)) downloaded in the current folder. Then run:
```
./extract.py -i "czech-republic-latest.osm.pbf" -a "Praha" -o "../data/poi/praha.csv"
```
So far, there are areas defined for *Praha* and *Brno*.

To add a new area, add the coordinates of top-left corner and right-bottom corner to the list `areas` in `extract.py`.

Be aware that the program creates a node cache for the area and uses it in subsequent runs.

### Add a new list of places / words
Create a CSV file containing a column `name`. Places can also contain columns `id`, `lat` (latitude), `lon` (longitude) and `type` ("node", "way", "area"), but for now they are pretty useless.
