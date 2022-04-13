# Interpolated character-level n-gram language model #

Scripts to train and score text with an n-gram language model using
interpolated smoothing.

## 1. Model training ##

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

## 2. Scoring data ##

For scoring data, use the `scorer.py` script. The simplest usage is:

```bash
cat some_data.txt | ./scorer.py model.pkl > scores.txt
```

When scoring finishes, `scores.txt` should have the same number of lines as
`some_data.txt`, one (negative) floating point number per line, representing
the score (which is the log likelihood of the input line as assigned by the
model).
