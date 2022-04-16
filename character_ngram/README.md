# Interpolated character-level n-gram language model #

Scripts to train and score text with an n-gram language model using
interpolated smoothing.

## Model training ##

To train a model, first get training and heldout datasets. Heldout data should
not overlap with the training data. Assuming you have plaintext training corpora
`train.txt` and `heldout.txt`, you can start the training using:

```bash
./train_ngrams.py train.txt model.pkl heldout.txt
```

This will train the model and save it into `model.pkl`.

There are various options available, you can list them all by typing:

```bash
./train_ngrams.py --help
```

### Converting to precalculated model

You can convert the model to a format suitable for the fast `jmc` module
and command-line tool. Build the portable model file with pre-computed
losses:

    ./ngram2jmc < model.pkl > model.jmc

## Preprocessing data

The `scorer.py` command-line tool performs the preprocessing based on
its input arguments.

For fain-grained preprocessing, you can use the `jmc` tool as a filter.
Currently, available filters are:

### Remove diacritics

To remove diacritics, leaving only Latin characters without numerals,
pipe the data like this:

    cat some_data.txt | ./jmc latin > preprocessed.txt

### Transliterate to Latin

The `latin` subcommand ignores characters that are not based on Latin,
like Unicode Roman numerals or Cyrillic. To deal with them, you might
find useful the `alpha` subcommand, which transliterates into Latin
(without numerals).

## Scoring data ##

For scoring data, use the `scorer.py` script. The simplest usage is:

```bash
cat some_data.txt | ./scorer.py model.pkl > scores.txt
```

When scoring finishes, `scores.txt` should have the same number of lines as
`some_data.txt`, one (negative) floating point number per line, representing
the score (which is the log likelihood of the input line as assigned by the
model).

### Efficient scoring

Alternatively, you can use the `jmc` module that does the same task, but
more efficiently:

    cat some_data.txt | ./jmc loss model.jmc > losses.txt

(Note that the command returns values of the loss function, which is
just the negative of score, and therefore always positive.)

## Sorting data based on score

To sort data based on score of each line, issue

    cat some_data.txt | ./jmc sort model.jmc > sorted.txt
