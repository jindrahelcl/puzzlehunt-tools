# Primitive character-level language model based on bigram statistics

## Runtime dependencies

The runtime dependencies are fairly simple:

 * Python 3

## Training

Before using this tool, it must be trained like this:

    ./bicount < source.txt > model.bin

The input file `source.txt` should consist of one training set per line.
The tool is quite good at converting Unicode to ASCII, but be sure to run
it in a correctly set locale environment (to get line endings and character
encoding right).

## Mundane usage

Typically, you will use `bisort` on an output of your script that returns
solution candidates of a puzzle, one at a line. `bisort`'s job is then to sort
the data set for you, by relevance within the specified language model.

    ./bisort model.bin < input.txt

## Training from OpenStreetMap

Along with this tool, there is shipped a ready-to-use solution for obtaining
street name data from OpenStreetMap as a base for training.

Simply issuing a `make` inside the `bigram_model` directory should lead to
creation of model files for three important Central European cities.
For detailed information, read the following paragraphs.

### Disk space requirements

Depending on the configuration (see below), the compilation step will download
several OpenStreetMap regions which are needed throughout the compilation.
At the time of writing, the requirements have been around 300 MiB of temporary
disk space.

After compilation is done, you can safely delete the downloaded intermediary
files by issuing `make clean` *inside the `osmnames` directory*.

### Compile-time dependencies

Make sure that the `bigram_model` directory is placed to the same parent
directory as `osmnames`. The compile-time dependencies are inherited from
the `osmnames` tool:

 * GNU Make
 * Python 3
 * Osmosis
 * cURL command-line utility
 * Unidecode Python 3 package

### Configuration

Before invoking `make`, you may wish to specify cities or other administrative
areas that you want to compile models for. This is done by editing the file
`osmnames/cityconf.mk`.

Be sure to specify the same administrative level that OpenStreetMap uses for
the city of interest; these values are country-cpecific and are documented
in the OpenStreetMap Wiki:
<https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative>.
