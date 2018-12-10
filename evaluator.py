
# NLP algorithm evaluator

# Imports
import re

from os import listdir
from os.path import isfile, join


# Define file names to have
filenames = []


# Method to read the file names
def readFileNames():
    filenames = [f for f in listdir("tagged/") if isfile(join("tagged/", f))]
    return filenames


# Method to clean tags from string
def clean_tags(s):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', s)
    return cleantext


# Find words by the given tag in the content
def find_by_tag(content, tag):
    # Define tags
    start_tag = "<" + tag + ">"
    end_tag = "</" + tag + ">"

    # Define regular expression to find tag
    pattern = re.compile(start_tag + "(.*?)" + end_tag)

    # Define list to return
    returnList = []

    # Iterate through all found tagged words
    for a in re.findall(pattern, content):
        returnList.append(clean_tags(a))

    # Return the return list
    return returnList

# Method to get all measures like TP, FP and FN
def get_measures(tagged, test):
    # Define true positive
    tp = 0

    to_pop = []

    # Find true positives
    for tag in tagged:
        if tag in test:
            tp += 1
            to_pop.append(tag)

    for tag in to_pop:
        if tag in tagged:
            tagged.pop(tagged.index(tag))
        if tag in test:
          test.pop(test.index(tag))

    # Calculate false positives and negatives
    fp = len(test)
    fn = len(tagged)

    # Return triplet
    return (tp, fp, fn)


# Main code
if __name__ == '__main__':
    # Read the file names
    filenames = readFileNames()

    # TEMPORARY
    # filenames = ['303.txt']m

    # Tags we have
    tags = ["stime", "etime", "location", "speaker", "paragraph", "sentence"]

    # Define total tp, fp and fn for all tags
    mapTagEval = {}
    for tag in tags:
        mapTagEval[tag] = {}
        mapTagEval[tag]['tp'] = 0
        mapTagEval[tag]['fp'] = 0
        mapTagEval[tag]['fn'] = 0

    # Define global true and false positives and negatives
    total_tp = 0
    total_fp = 0
    total_fn = 0

    # For each file in the folders
    for file in filenames:
        # Get both paths
        taggedFilePath   = "tagged/" + file
        test_taggedFilePath = "test_tagged/" + file

        # Get contents
        taggedContent   = open(taggedFilePath, "r").read()
        test_taggedContent = open(test_taggedFilePath, "r").read()

        for tag in tags:
            # Get the tagged content
            taggedTag   = find_by_tag(taggedContent, tag)
            test_taggedTag = find_by_tag(test_taggedContent, tag)

            # Calculate true positives, false positives and negatives
            tp, fp, fn = get_measures(taggedTag, test_taggedTag)
            total_tp += tp
            total_fp += fp
            total_fn += fn

            # Calculate all by tag
            mapTagEval[tag]['tp'] += tp
            mapTagEval[tag]['fp'] += fp
            mapTagEval[tag]['fn'] += fn

            # Show what are the false values
            # if tag is "speaker" and fp > 0:
            #     print(file + "fp" + str(fp))
            # if tag is "speaker" and fn > 0:
            #     print(file + "fn" + str(fn))

    # Define accuracy, precision, recall and f1 measure
    accuracy = 0
    precision = 0
    recall = 0
    f1 = 0

    # Calculate accuracy
    if (total_tp + total_fp + total_fn) == 0:
        accuracy = 100
    else:
        accuracy = total_tp / (total_tp + total_fp + total_fn) * 100

    # Calculate precision
    if (total_tp + total_fp) == 0:
        precision = 100
    else:
        precision = total_tp / (total_tp + total_fp) * 100

    # Calculate recall
    if (total_tp + total_fn) == 0:
        recall = 100
    else:
        recall = total_tp / (total_tp + total_fn) * 100

    # Calculate the f1 measure
    if (precision + recall) == 0:
        f1 = 100
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    # Print header for displaying
    print("TAG                   Accuracy    Precision   Recall      F1 measure")
    print("total" + (10 - len("total")) * ' ' + "             {a:.2f}%      {p:.2f}%      {r:.2f}%      {f:.2f}%".format(a=accuracy, p=precision, r=recall, f=f1))

    # For all tags
    for tag in tags:
        # Define accuracy, precision, recall and f1 measure
        accuracy = 0
        precision = 0
        recall = 0
        f1 = 0

        # Calculate accuracy
        if (mapTagEval[tag]['tp'] + mapTagEval[tag]['fp'] + mapTagEval[tag]['fn']) == 0:
            accuracy = 100
        else:
            accuracy = mapTagEval[tag]['tp'] / (mapTagEval[tag]['tp'] + mapTagEval[tag]['fp'] + mapTagEval[tag]['fn']) * 100

        # Calculate precision
        if (mapTagEval[tag]['tp'] + mapTagEval[tag]['fp']) == 0:
            precision = 100
        else:
            precision = mapTagEval[tag]['tp'] / (mapTagEval[tag]['tp'] + mapTagEval[tag]['fp']) * 100

        # Calculate recall
        if (mapTagEval[tag]['tp'] + mapTagEval[tag]['fn']) == 0:
            recall = 100
        else:
            recall = mapTagEval[tag]['tp'] / (mapTagEval[tag]['tp'] + mapTagEval[tag]['fn']) * 100

        # Calculate the f1 measure
        if (precision + recall) == 0:
            f1 = 100
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        # Print values for each tag
        print(tag + (10 - len(tag)) * ' ' + "             {a:.2f}%      {p:.2f}%      {r:.2f}%      {f:.2f}%".format(a=accuracy, p=precision, r=recall, f=f1))

