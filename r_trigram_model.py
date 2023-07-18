import sys
from collections import defaultdict
import math
import random
import os
import os.path

"""
COMS W4705 - Natural Language Processing - Spring 2023
Programming Homework 1 - Trigram Language Models
Name: Jishan Desai
unid : jd3895
Prof: Daniel Bauer
"""


def corpus_reader(corpusfile, lexicon=None):
    with open(corpusfile, 'r') as corpus:
        for line in corpus:
            if line.strip():
                sequence = line.lower().strip().split()
                if lexicon:
                    yield [word if word in lexicon else "UNK" for word in sequence]
                else:
                    yield sequence


def get_lexicon(corpus):
    word_counts = defaultdict(int)
    for sentence in corpus:
        for word in sentence:
            word_counts[word] += 1
    return set(word for word in word_counts if word_counts[word] > 1)


def get_ngrams(sequence, n):
    """
    COMPLETE THIS FUNCTION (PART 1)
    Given a sequence, this function should return a list of n-grams, where each n-gram is a Python tuple.
    This should work for arbitrary values of n >= 1 
    """
    ans_list = []
    if n < 1:
        raise Exception("Enter n greater than or equal to 1")
    if n == 1:
        ans_list.append(("START",))
        for i in sequence:
            ans_list.append((i,))
        ans_list.append(("STOP",))
        return ans_list
    for i in range(len(sequence)):
        start_paddings = abs(i - n + 1)
        if start_paddings == 0:
            break
        start_padding_list = ["START"] * start_paddings
        start_padding_list.extend(sequence[0:(i + 1)])
        res = tuple(start_padding_list)
        ans_list.append(res)
    for i in range(len(sequence)):
        if (i + n) < (len(sequence) + 1):
            list_one = sequence[i:i + n]
            ans_list.append(tuple(list_one))
        else:
            temp = sequence[i:len(sequence)]
            temp.append("STOP")
            while len(temp) < n:
                temp.insert(0, "START")
            ans_list.append(tuple(temp))
            break
    return ans_list


class TrigramModel(object):

    def __init__(self, corpusfile):
        # Iterate through the corpus once to build a lexicon
        generator = corpus_reader(corpusfile)
        self.lexicon = get_lexicon(generator)
        self.lexicon.add("UNK")
        self.lexicon.add("START")
        self.lexicon.add("STOP")
        self.total_words = 0
        self.total_sentences = 0
        # Now iterate through the corpus again and count ngrams
        generator = corpus_reader(corpusfile, self.lexicon)
        self.count_ngrams(generator)

    def count_ngrams(self, corpus):
        """
        COMPLETE THIS METHOD (PART 2)
        Given a corpus iterator, populate dictionaries of unigram, bigram,
        and trigram counts. 
        """

        self.unigramcounts = defaultdict(int)  # might want to use default-dict or Counter instead
        self.bigramcounts = defaultdict(int)
        self.trigramcounts = defaultdict(int)
        for sentence in corpus:
            self.total_sentences += 1
            self.total_words += len(sentence) + 1
            for t in get_ngrams(sentence, 1):
                # if t[0] != "START":
                #     #self.total_words += 1
                self.unigramcounts[t] += 1
            for t in get_ngrams(sentence, 2):
                self.bigramcounts[t] += 1
            for t in get_ngrams(sentence, 3):
                self.trigramcounts[t] += 1
        return

    def raw_trigram_probability(self, trigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) trigram probability
        """
        joint_count = self.trigramcounts[trigram]
        bi_count = self.bigramcounts[trigram[0:2]]
        raw_prob = 0.0
        if trigram[0] == "START" and trigram[1] == "START":
            if trigram[2] == "START":
                return 0.0
            raw_prob = joint_count / self.total_sentences
        elif bi_count == 0:
            raw_prob = self.raw_unigram_probability(trigram[2:])
        elif bi_count > 0:
            raw_prob = joint_count / bi_count
        return raw_prob

    def raw_bigram_probability(self, bigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) bigram probability
        """
        joint_count = self.bigramcounts[bigram]
        raw_prob = 0.0
        if bigram[0] == "START":
            if bigram[1] == "START":
                return raw_prob
            raw_prob = joint_count / self.total_sentences
        elif bigram[0] != "START":
            unigram_count = self.unigramcounts[bigram[0:1]]
            raw_prob = joint_count / unigram_count
        return raw_prob

    def raw_unigram_probability(self, unigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) unigram probability.
        """
        # hint: recomputing the denominator every time the method is called
        # can be slow! You might want to compute the total number of words once,
        # store in the TrigramModel instance, and then re-use it.
        raw_prob = 0.0
        if unigram[0] == "START":
            return raw_prob
        raw_prob = self.unigramcounts[unigram] / self.total_words
        return raw_prob

    def generate_sentence(self, t=20):
        """
        COMPLETE THIS METHOD (OPTIONAL)
        Generate a random sentence from the trigram model. t specifies the
        max length, but the sentence may be shorter if STOP is reached.
        """
        return result

    def smoothed_trigram_probability(self, trigram):
        """
        COMPLETE THIS METHOD (PART 4)
        Returns the smoothed trigram probability (using linear interpolation).
        """
        lambda1 = 1 / 3.0
        lambda2 = 1 / 3.0
        lambda3 = 1 / 3.0
        smoothed_prob = lambda1 * self.raw_trigram_probability(trigram) + lambda2 * self.raw_bigram_probability(
            trigram[1:]) + lambda3 * self.raw_unigram_probability(trigram[2:])
        return smoothed_prob

    def sentence_logprob(self, sentence):
        """
        COMPLETE THIS METHOD (PART 5)
        Returns the log probability of an entire sequence.
        """
        n_grams = get_ngrams(sentence, 3)
        log_prob = 0.0
        for i in n_grams:
            log_prob += math.log2(self.smoothed_trigram_probability(i))
        return log_prob

    def perplexity(self, corpus):
        """
        COMPLETE THIS METHOD (PART 6) 
        Returns the log probability of an entire sequence.
        """
        sum = 0.0
        words = 0
        for sentence in corpus:
            words += (len(sentence) + 1)
            sum += self.sentence_logprob(sentence)
        const = 1 / words
        l = const * sum

        return 2 ** (-l)


def essay_scoring_experiment(training_file1, training_file2, testdir1, testdir2):
    model1 = TrigramModel(training_file1)
    model2 = TrigramModel(training_file2)

    total = 0
    correct = 0

    for f in os.listdir(testdir1):
        pp = model1.perplexity(corpus_reader(os.path.join(testdir1, f), model1.lexicon))
        pp2 = model2.perplexity(corpus_reader(os.path.join(testdir1, f), model2.lexicon))
        if pp < pp2:
            correct = correct + 1
        total = total + 1
    for f in os.listdir(testdir2):
        pp2 = model2.perplexity(corpus_reader(os.path.join(testdir2, f), model2.lexicon))
        pp = model1.perplexity(corpus_reader(os.path.join(testdir2, f), model1.lexicon))
        if pp2 < pp:
            correct = correct + 1
        total = total + 1
    return correct / total


if __name__ == "__main__":
    model = TrigramModel("test.txt")
    # print(get_ngrams(["hi", "how", "are","you","doing"], 1))
    # print(get_ngrams(["hi", "how", "are", "you", "doing"], 2))
    # print(get_ngrams(["hi", "how", "are", "you", "doing"], 3))
    # print(get_ngrams(["hi", "how", "are", "you", "doing"], 4))
    # print(get_ngrams(["hi", "how", "are", "you", "doing"], 5))
    # print(get_ngrams(["hi", "how", "are", "you", "doing"], 15))
    # dev_corpus = corpus_reader(sys.argv[2], model.lexicon)
    # pp = model.perplexity(dev_corpus)
    # print(pp)
    # print(model.trigramcounts[('START', 'START', 'the')])
    # print(model.raw_unigram_probability(('START',)))
    # print(model.raw_bigram_probability(('START', 'the')))
    # print(model.raw_trigram_probability(('START', 'START', 'for')))
    # print(model.raw_trigram_probability(('START', 'but', ','))) #on 88.txt
    # print(model.raw_trigram_probability(('group','tour','alone')))
    # print(model.smoothed_trigram_probability(('group','tour','alone')))
    # print(model.sentence_logprob(['when', 'i', 'went', 'to', 'UNK', 'by', 'UNK', ',', 'i', 'UNK', 'really', 'many', 'people', 'there', '.']))
    #
# acc = essay_scoring_experiment('train_high.txt', 'train_low.txt', 'test_high', 'test_low')
# print(acc)
# print(model.trigramcounts[('UNK','UNK','UNK')])
# print(model.bigramcounts[('UNK','UNK')])
# print(model.unigramcounts['UNK'])
# print(model.raw_trigram_probability(('UNK','UNK','UNK')))
# model.trigramcounts[('START', 'START', 'the')]
# print(get_ngrams(["natural", "language", "processing"], 1))
# put test code here...
# or run the script from the command line with
# $ python -i trigram_model.py [corpus_file]
# >>>
#
# you can then call methods on the model instance in the interactive
# Python prompt.


# Essay scoring experiment:
# acc = essay_scoring_experiment('train_high.txt', 'train_low.txt', "test_high", "test_low")
# print(acc)
