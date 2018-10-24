import os
import sys
import collections
import re
import math
import copy
import time


training_set = dict()
test_set = dict()
without_stop_training_set = dict()
without_stop_test_set = dict()
stop_words = []
training_set_vocab = []
without_stop_training_set_vocab = []
weights = {'w0': 0.0}
without_stop_weights = {'w0': 0.0}
cl = ["ham", "spam"]
alpha = .005
iteration_count = 100


def make_data_set(storage_dict, directory, true_class):
    for doc in os.listdir(directory):
        dir_path = os.path.join(directory, doc)
        if os.path.isfile(dir_path):
            with open(dir_path, 'r') as text_file:
                text = text_file.read()
                storage_dict.update({dir_path: Doc(text, get_word_freq(text), true_class)})


def get_vocab(data_set):
    v = []
    for i in data_set:
        for j in data_set[i].get_word_freq():
            if j not in v:
                v.append(j)
    return v


def remove_stop_words(stops, data_set):
    filtered_data_set = copy.deepcopy(data_set)
    for i in stops:
        for j in filtered_data_set:
            if i in filtered_data_set[j].get_word_freq():
                del filtered_data_set[j].get_word_freq()[i]
    return filtered_data_set


def get_word_freq(text):
    bags = collections.Counter(re.findall(r'\w+', text))
    return dict(bags)


def learn_weights(training, wts, iterations, lam):
    for x in range(0, iterations):
        for w in wts:
            sm = 0.0
            for i in training:
                y_field = 0.0
                if training[i].get_true_class() == cl[1]:
                    y_field = 1.0
                if w in training[i].get_word_freq():
                    cond_prob = calculate_cond_prob(cl[1], wts, training[i])
                    sm += float(training[i].get_word_freq()[w]) * (y_field - cond_prob)
            wts[w] += ((alpha * sm) - (alpha * float(lam) * wts[w]))


def calculate_cond_prob(class_prob, wts, doc):

    if class_prob == cl[0]:
        sum_wx_0 = wts['w0']
        for i in doc.get_word_freq():
            if i not in wts:
                wts[i] = 0.0
            sum_wx_0 += wts[i] * float(doc.get_word_freq()[i])
        return 1.0 / (1.0 + math.exp(float(sum_wx_0)))

    elif class_prob == cl[1]:
        sum_wx_1 = wts['w0']
        for i in doc.get_word_freq():
            if i not in wts:
                wts[i] = 0.0
            sum_wx_1 += wts[i] * float(doc.get_word_freq()[i])
        return math.exp(float(sum_wx_1)) / (1.0 + math.exp(float(sum_wx_1)))


def apply_lr(data_instance, weights_param):
    score = dict()
    score[0] = calculate_cond_prob(cl[0], weights_param, data_instance)
    score[1] = calculate_cond_prob(cl[1], weights_param, data_instance)
    if score[1] > score[0]:
        return cl[1]
    else:
        return cl[0]


class Doc:
    text = ""
    word_freq = {'w0': 1.0}

    actual_class = ""
    predicted_class = ""

    def __init__(self, text, counter, true_class):
        self.text = text
        self.word_freq = counter
        self.actual_class = true_class

    def get_text(self):
        return self.text

    def get_word_freq(self):
        return self.word_freq

    def get_true_class(self):
        return self.actual_class

    def get_learned_class(self):
        return self.predicted_class

    def set_learned_class(self, guess):
        self.predicted_class = guess


def process(training_spam_dir, training_ham_dir, test_spam_dir, test_ham_dir, lambda_constant, stop_words_path):
    start = time.time()
    make_data_set(training_set, training_spam_dir, cl[1])
    make_data_set(training_set, training_ham_dir, cl[0])
    make_data_set(test_set, test_spam_dir, cl[1])
    make_data_set(test_set, test_ham_dir, cl[0])
    pen = lambda_constant

    with open(stop_words_path, 'r') as txt:
        stop_word = (txt.read().splitlines())

    filtered_training = remove_stop_words(stop_word, training_set)
    filtered_test = remove_stop_words(stop_word, test_set)

    training_set_voc = get_vocab(training_set)
    filtered_training_set_voc = get_vocab(filtered_training)

    for i in training_set_voc:
        weights[i] = 0.0
    for i in filtered_training_set_voc:
        without_stop_weights[i] = 0.0

    learn_weights(training_set, weights, iteration_count, pen)
    learn_weights(filtered_training, without_stop_weights, iteration_count, pen)

    correct_guesses = 0.0
    for i in test_set:
        test_set[i].set_learned_class(apply_lr(test_set[i], weights))
        if test_set[i].get_learned_class() == test_set[i].get_true_class():
            correct_guesses += 1.0

    correct_guesses_filtered = 0.0
    for i in filtered_test:
        filtered_test[i].set_learned_class(apply_lr(filtered_test[i], without_stop_weights))
        if filtered_test[i].get_learned_class() == filtered_test[i].get_true_class():
            correct_guesses_filtered += 1.0

    acc = float(correct_guesses) / float(len(test_set))
    print "Correct guesses:", correct_guesses, "/", len(test_set)
    print "Accuracy with stop words: ", math.ceil(acc * 100000) / 1000
    print

    acc = float(correct_guesses_filtered) / float(len(filtered_test))
    print "Correct guesses: ", correct_guesses_filtered, "/", len(filtered_test)
    print "Accuracy without stop words: ", math.ceil(acc * 100000) / 1000
    end = time.time()
    print "Time Taken: ", (end - start)


if __name__ == '__main__':
    process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
