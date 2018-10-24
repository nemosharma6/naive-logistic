import os
import math
import sys


def apply_naive(spam_path, ham_path, test_spam_path, test_ham_path, stop_words_file_path):
    ham_files = []
    spam_files = []
    test_ham_files = []
    test_spam_files = []
    stop_words = open(stop_words_file_path).read().split()

    for i in os.listdir(ham_path):
        if i.endswith('.txt'):
            ham_files.append(open(ham_path + "/" + i))

    for i in os.listdir(spam_path):
        if i.endswith('.txt'):
            spam_files.append(open(spam_path + "/" + i))

    distinct_words = set()
    dic_ham = {}
    dic_spam = {}
    count_ham_files = 0
    count_spam_files = 0
    count_ham_words = 0
    count_spam_words = 0
    count_ham_words_without_stop = 0
    count_spam_words_without_stop = 0

    for i in ham_files:
        values = i.read().split()
        count_ham_files += 1
        count_ham_words += len(values)
        for j in values:
            if j not in stop_words:
                count_ham_words_without_stop += 1
            distinct_words.add(j)
            if j in dic_ham:
                v = dic_ham[j]
                dic_ham[j] = v + 1
            else:
                dic_ham[j] = 1

    for i in spam_files:
        values = i.read().split()
        count_spam_files += 1
        count_spam_words += len(values)
        for j in values:
            if (j not in stop_words) & (not j.isdigit()):
                count_spam_words_without_stop += 1
            distinct_words.add(j)
            if j in dic_spam:
                v = dic_spam[j]
                dic_spam[j] = v + 1
            else:
                dic_spam[j] = 1

    distinct_words_without_stop = distinct_words - set(stop_words)
    print len(distinct_words), len(distinct_words_without_stop)
    count_test_ham_words = 0
    count_test_spam_words = 0
    test_ham_files_count = 0
    test_spam_files_count = 0

    for i in os.listdir(test_ham_path):
        if i.endswith('.txt'):
            test_ham_files_count += 1
            test_ham_files.append(open(test_ham_path + "/" + i))

    for i in os.listdir(test_spam_path):
        if i.endswith('.txt'):
            test_spam_files_count += 1
            test_spam_files.append(open(test_spam_path + "/" + i))

    for i in test_ham_files:
        values = i.read().split()
        count_test_ham_words += len(values)

    for i in test_spam_files:
        values = i.read().split()
        count_test_spam_words += len(values)

    ham_pos_count = 0
    spam_pos_count = 0

    for i in test_ham_files:
        i.seek(0)
        values = i.read().split()
        pr_ham = 0.0
        pr_spam = 0.0
        for j in values:
            ct_ham = 1.0
            ct_spam = 1.0
            if j in dic_ham:
                ct_ham = dic_ham[j] + 1.0
            if j in dic_spam:
                ct_spam = dic_spam[j] + 1.0
            pr = ct_ham / (count_ham_words + len(distinct_words) * 1.0)
            pr_ham = pr_ham + math.log(pr)
            pr = ct_spam / (count_spam_words + len(distinct_words) * 1.0)
            pr_spam = pr_spam + math.log(pr)
        if pr_ham + math.log(test_ham_files_count) > pr_spam + math.log(test_spam_files_count):
            ham_pos_count += 1
        # if pr_ham > pr_spam:
        #     ham_pos_count += 1

    for i in test_spam_files:
        i.seek(0)
        values = i.read().split()
        pr_ham = 0.0
        pr_spam = 0.0
        for j in values:
            ct_ham = 1.0
            ct_spam = 1.0
            if j in dic_ham:
                ct_ham = dic_ham[j] + 1.0
            if j in dic_spam:
                ct_spam = dic_spam[j] + 1.0
            pr = ct_ham / (count_ham_words + len(distinct_words) * 1.0)
            pr_ham = pr_ham * math.log(pr)
            pr = ct_spam / (count_spam_words + len(distinct_words) * 1.0)
            pr_spam = pr_spam * math.log(pr)
        if pr_ham + math.log(test_ham_files_count) <= pr_spam + test_spam_files_count:
            spam_pos_count += 1
        # if pr_ham <= pr_spam:
        #     spam_pos_count += 1

    total_pos_count = ham_pos_count + spam_pos_count
    acc = (total_pos_count * 1.0) / (test_ham_files_count + test_spam_files_count)
    print "Correct guesses: ", total_pos_count, "/", (test_ham_files_count + test_spam_files_count)
    print "Accuracy with stop words : ", (math.ceil(acc * 100000) / 1000)

    #####################################################################################################

    # Removing Stop Words

    ham_pos_count = 0
    spam_pos_count = 0

    for i in test_ham_files:
        i.seek(0)
        values = i.read().split()
        pr_ham = 0.0
        pr_spam = 0.0
        for j in values:
            if j in stop_words:
                continue
            ct_ham = 1.0
            ct_spam = 1.0
            if j in dic_ham:
                ct_ham = dic_ham[j] + 1.0
            if j in dic_spam:
                ct_spam = dic_spam[j] + 1.0
            pr = ct_ham / (count_ham_words_without_stop + len(distinct_words_without_stop) * 1.0)
            pr_ham = pr_ham + math.log(pr)
            pr = ct_spam / (count_spam_words_without_stop + len(distinct_words_without_stop) * 1.0)
            pr_spam = pr_spam + math.log(pr)
        if pr_ham + math.log(test_ham_files_count) > pr_spam + math.log(test_spam_files_count):
            ham_pos_count += 1
        # if pr_ham > pr_spam:
        #     ham_pos_count += 1

    for i in test_spam_files:
        i.seek(0)
        values = i.read().split()
        pr_ham = 0.0
        pr_spam = 0.0
        for j in values:
            if j in stop_words:
                continue
            ct_ham = 1.0
            ct_spam = 1.0
            if j in dic_ham:
                ct_ham = dic_ham[j] + 1.0
            if j in dic_spam:
                ct_spam = dic_spam[j] + 1.0
            pr = ct_ham / (count_ham_words_without_stop + len(distinct_words_without_stop) * 1.0)
            pr_ham = pr_ham * math.log(pr)
            pr = ct_spam / (count_spam_words_without_stop + len(distinct_words_without_stop) * 1.0)
            pr_spam = pr_spam * math.log(pr)
        if pr_ham + math.log(test_ham_files_count) <= pr_spam + test_spam_files_count:
            spam_pos_count += 1
        # if pr_ham <= pr_spam:
        #     spam_pos_count += 1

    total_pos_count = ham_pos_count + spam_pos_count
    acc = (total_pos_count * 1.0) / (test_ham_files_count + test_spam_files_count)
    print "Correct guesses: ", total_pos_count, "/", (test_ham_files_count + test_spam_files_count)
    print "Accuracy without stop words: ", math.ceil(acc * 100000) / 1000


if __name__ == '__main__':
    apply_naive(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
