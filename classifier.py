# Michael Wheatman
# Matt Cotter
import sys
import re
import os
import random
import math
import cPickle
from collections import defaultdict


# This is an adaptation of the tokenizer in the book.
def tokenize(source_text):
    clitic = re.compile("('|:|-|'S|'D|'M|'LL|'RE|'VE|N'T|'s|'d|'m|'ll|'re|'ve|n't)")
    alwayssep = re.compile(r"([~\?!()\";?|\\`])")
    frontcommas = re.compile(r'(,)([^0-9])')
    backcommas = re.compile(r'([^0-9])(,)')
    singlequotes = re.compile(r"([^A-Za-z])(')")
    acronym = re.compile(r'([A-Z-Z]\.([A-ZA-Z]\.)+|[A-Z][bcdfghj-nptvxz]+\.)')
    period = re.compile(r'\.')
    number = re.compile(r'([0-9][0-9,]*[0-9])')

    # we use \x05 as a character to split on and remove
    abbr = set(["Co.", "Dr.", "Mr.", "Mrs.", "Ms.", "Esq.", "St.", "Ln.",
                "Rd.", "Ave.", "Blvd.", "co.", "dr.", "mr.", "mrs.", "ms.",
                "esq.", "st.", "ln.", "rd.", "ave.", "blvd."])
    # convert -- or 'em dash' to ~
    source_text = re.sub(r'--|\xE2\x80\x94', '~', source_text)

    source_text = re.sub(r'_', '', source_text)
    source_text = alwayssep.sub(' \\1 ', source_text)
    source_text = frontcommas.sub(' \\1 \\2', source_text)
    source_text = backcommas.sub('\\1 \\2 ', source_text)
    source_text = number.sub(' <numeric> ', source_text)
    source_text = singlequotes.sub('\\1 \\2 ', source_text)
    source_text = clitic.sub(' \\1 ', source_text)
    # condense whitespace
    source_text = re.sub(r'\s+', ' ', source_text)
    # split in to tokens
    words = source_text.split(' ')
    # this new list will be built as we go.
    # We still need to decide what to do with periods.
    new_words = ['<begin>']
    for word in words:
        if word not in abbr and not acronym.match(word):
            word = period.sub(' . <begin> ', word)
            new_words += word.split(' ')
        elif word in '.!?':
            new_words.append(word)
            new_words.append('<begin>')
        else:
            new_words.append(word)
    # filter out empty strings
    new_words = [x for x in new_words if x != '' and x != '"']
    # Remove Capitolization
    vocab = set(new_words)
    for i, w in enumerate(new_words):
        if w.lower() != w and w.lower() in vocab:
            new_words[i] = w.lower()
    return new_words


def sentence_tokens(token_list):
    ret = []
    current = []
    for i, t in enumerate(token_list):
        if t == '<begin>':
            ret.append(current)
            current = []
        else:
            current.append(t)
    return ret


def devSetCreator(input_file, filename, path='training'):
    if not os.path.exists(path):
        os.makedirs(path)
    _, _, filename = filename.rpartition('/') if '/' in filename else ('', '', filename)
    devFile = path + "/devSet_" + filename
    trainFile = path + "/trainSet_" + filename
    d = open(devFile, "w")
    t = open(trainFile, "w")
    tokens = tokenize(input_file.read())
    sentences = sentence_tokens(tokens)
    for s in sentences:
        sent = ' '.join(s)
        if random.randrange(0, 10) == 0:
            d.write(sent+'\n')
        else:
            t.write(sent+'\n')


# returns a dictionary with a default value of another instance of this kind of
# dictionary and the initial value of the dictionary at key 0 is 0.
def get_count_dict():
    d = defaultdict(get_count_dict)
    d[0] = 0
    return d


# Creates a dictionary that will contain a dictionary for each unigram,
# which then contains a dictionary holding the second element of a bigram,
# each bi-gram consists of a dictionary that contains the third element of the
# trigram started by the word "t".
def get_counts(token_list):
    counts = get_count_dict()
    for i, t in enumerate(token_list):
        counts[0] += 1
        counts[t][0] += 1
        if i + 1 < len(token_list):
            counts[t][token_list[i+1]][0] += 1
        if i + 2 < len(token_list):
            counts[t][token_list[i+1]][token_list[i+2]][0] += 1
    return counts


def prob(counts, w1, w2=None, w3=None):
    if w3 is None:
        if w2 is None:
            return 0.0 if counts[w1][0] == 0 else float(counts[w1][0]) / counts[0]
        else:
            return 0.0 if counts[w1][w2][0] == 0 \
                else float(counts[w1][w2][0]) / counts[w1][0]
    else:
        return 0.0 if counts[w1][w2][w3][0] == 0 \
            else float(counts[w1][w2][w3][0]) / counts[w1][w2][0]


def prob_star(counts, w1, w2, w3):
    # These were chosen empirically via repeated testing.
    lmbd3 = 0.9
    lmbd2 = 0.07
    lmbd1 = 0.025
    lmbd0 = 0.005
    # calculations done in log probs
    return math.log(lmbd3 * prob(counts, w1, w2, w3) +
                    lmbd2 * prob(counts, w1, w2) +
                    lmbd1 * prob(counts, w1) + lmbd0)


# creates the language model for each author
def create_models():
    models = []
    for author in ['Austen', 'Christie', 'Dickens', 'Doyle', 'Grimm', 'Thoreau',
                   'Whitman', 'Wilde']:
        source_text = ''
        # This is so we can use the same python file for our
        # training set as the one we turn in.
        try:
            input_file = open('training/trainSet_'+author.lower()+'.txt')
            source_text = input_file.read()
            input_file.close()
        except Exception:
            try:
                input_file = open(author.lower()+'.txt')
                source_text = input_file.read()
                input_file.close()
            except Exception:
                print 'Error: could not open the training sets.'
        tokens = tokenize(source_text)
        counts = get_counts(tokens)
        models.append((author, counts))
    return models


def get_perplexity(model, tokens):
    prob = 0.0
    token_list = tokens + ['.', '.']
    for i, t in enumerate(token_list[:-2]):
        prob += prob_star(model, t, token_list[i+1], token_list[i+2])
    return math.pow(math.e, prob * (-1.0/len(tokens)))


def main():
    input_tokens = tokenize(sys.stdin.read())
    all_models = []
    try:
        f = open('models.pickle', 'r')
        all_models = cPickle.load(f)
        f.close()
    except Exception:
        all_models = create_models()
        f = open('models.pickle', 'w+')
        cPickle.dump(all_models, f)
        f.close()
    min_perplex = ('fakename', 9999999999999)
    for author, model in all_models:
        p = get_perplexity(model, input_tokens)
        if p < min_perplex[1]:
            min_perplex = (author, p)
    print min_perplex[0]


if __name__ == '__main__':
    main()
