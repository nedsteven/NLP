import re
from os import listdir
from os.path import isfile, join

files = []
tags = ['stime', 'etime', 'sentence', 'paragraph', 'location' , 'speaker']
metrics = ['tp', 'fp', 'fn']
columns = 'Accuracy  |  Precision  |  Recall  |  F1'
values = {}


def initialise():
    for tag in tags:
        values[tag] = {}
        for metric in metrics:
            values[tag][metric] = 0


def read_files():
    files = [f for f in listdir('tagged/') if isfile(join('tagged/', f))]
    return files


def get_values(tagged, test, file, tag):
    tp = 0
    i = 0
    while i < len(tagged):
        if tagged[i] in test:
            tp += 1
            test.remove(tagged[i])
            tagged.remove(tagged[i])
            i = i - 1
        i += 1

    fp = len(tagged)
    fn = len(test)
    if fp > 0 or fn > 0:
        print('In file ' + file + ' on tag ' + tag)
        print(tagged)
        print(test)
        print()
    return tp, fp, fn


def get_contents(file):
    tagged_dir = 'tagged/'
    test_dir = 'test_tagged/'
    tagged_content = ''
    test_content = ''

    with open(tagged_dir + file, 'r') as f:
        tagged_content = f.read()
    with open(test_dir + file, 'r') as f:
        test_content = f.read()

    return tagged_content, test_content


def get_tokens(tagged_content, test_content, tag):

    tagged_tokens = []
    test_tokens = []

    start_tag = '<' + tag + '>'
    end_tag = '</' + tag + '>'
    regex = re.compile(start_tag + '(.*?)' + end_tag)

    tagged_tokens = re.findall(regex, tagged_content)
    test_tokens = re.findall(regex, test_content)

    for i in range(len(test_tokens)):
        test_tokens[i] = test_tokens[i].strip()
    for i in range(len(tagged_tokens)):
        tagged_tokens[i] = tagged_tokens[i].strip()

    return tagged_tokens, test_tokens
 

def compute_metrics(tp, fp, fn):
    accuracy = 0
    precision = 0
    recall = 0
    f1 = 0
    
    y = tp + fp + fn
    if y == 0:
        accuracy = 0
    else:
        accuracy = tp / y * 100
        
    # Compute precision
    y = tp + fp
    if y == 0:
        precision = 0
    else:
        precision = tp / y * 100
    # Compute recall
    # SUBJECT TO CHANGE
    y = tp + fn
    if y == 0:
        recall = 0
    else:
        recall = tp / y * 100

    # Compute f1
    y = precision + recall
    x = precision * recall
    if y == 0:
        f1 = 0
    else:
        f1 = 2 * x / y 

    return accuracy, precision, recall, f1 


if __name__ == '__main__':
    files = read_files()
    initialise()

    total_tp = 0
    total_fp = 0
    total_fn = 0

    #file = '319.txt'
    #tagged_content, test_content = get_contents(file)
    #for tag in tags:
     #       tagged_tokens, test_tokens = get_tokens(tagged_content, test_content, tag)
      #      tp, fp, fn = get_values(tagged_tokens, test_tokens)
    print('TAG' + ' ' * 12 + '|' + ' ' * 5 + columns)
    print('-' * 15 + '|' + '-' * (5 + len(columns)))

    for file in files:
        tagged_content = ''
        test_content = ''
        tagged_content, test_content = get_contents(file)

        for tag in tags:
            tagged_tokens, test_tokens = get_tokens(tagged_content, test_content, tag)
            tp, fp, fn = get_values(tagged_tokens, test_tokens, file, tag)
            values[tag]['tp'] += tp
            values[tag]['fp'] += fp
            values[tag]['fn'] += fn

    for tag in tags:
        total_tp += values[tag]['tp']
        total_fp += values[tag]['fp']
        total_fn += values[tag]['fn']
        accuracy, precision, recall, f1 = compute_metrics(values[tag]['tp'], values[tag]['fp'], values[tag]['fn'])
        print(tag + ' ' * (15 - len(tag)) + '|      ' + '{a:.2f}%   |   {p:.2f}%   |   {r:.2f}%   |   {d:.2f}%'.format(a=accuracy, p=precision, r=recall, d=f1))
    
    accuracy, precision, recall, f1 = compute_metrics(total_tp, total_fp, total_fn)
    print('total' + ' ' * 10 + '|      ' + '{a:.2f}%   |   {p:.2f}%   |   {r:.2f}%   |   {d:.2f}%'.format(a=accuracy, p=precision, r=recall, d=f1))
