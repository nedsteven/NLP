import gensim
import re
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from os import listdir
from os.path import isfile, join

categories = {
    'Sciences' : {
        'Computing' : ['Robotics', 'AI', 'Security', 'Databases', 'HCI', 'Hardware', 'Systems', 'Graphics'],
        'Physics' : ['Nuclear', 'Thermodynamics', 'Electromagnetism', 'Quantum', 'Relativity'],
        'Chemistry' : ['Analytical', 'Biochemistry', 'Inorganic', 'Organic', 'Physical'],
        'Mathematics' : ['Algebra', 'Geometry', 'Combinatorics', 'Analytics'],
        'Biology' : ['Anatomy', 'Zoology', 'Botany']
    },
    'Humanities' : {
        'Psychology' : ['Behavioural', 'Cognitive', 'Evolutionary', 'Educational', 'Forensic'],
        'Law' : ['Constitutional', 'Civil', 'Administrative', 'Procedural', 'Penal'],
        'Art' : ['Literature', 'Painting', 'Sculpture', 'Theatre', 'Music'],
        'Philosophy' : ['Metaphysics', 'Epistemology', 'Logic', 'Ethics', 'Aesthetics'],
        'Religion' : ['Historical', 'Missiology', 'Apologetics']
    }
}

tagged_path = 'untagged/'

best_category = {}

def get_keywords(file):
    keywords = []
    path = tagged_path + file
    content = ''

    with open(path, 'r') as f:
        content = f.read()
        re.sub(r'<(.*?)>', '', content)
        tagged_words = pos_tag(word_tokenize(content))
        for word, part in tagged_words:
            if part[0] == 'N' or part[0] == 'J':
                keywords.append(word)

    return keywords


def compute_score(categ, keywords, model):
    score = 0
    for keyword in keywords:
        try:
            score += model.similarity(keyword.lower(), categ.lower())
        except:
            pass
    if (len(keywords) > 0):
        return score * 100 / len(keywords)
    else:
        return 0


def get_most_likely(categs, keywords, model):
    best = ''
    best_score = 0
    for categ in categs:
        score = compute_score(categ, keywords, model)
        if score > best_score:
            best_score = score
            best = categ
    return best


if __name__ == '__main__':

    model = Word2Vec.load_word2vec_format('/home/projects/google-news-corpus/GoogleNews-vectors-negative300.bin', binary=True)
    print('Done loading')
    files = [f for f in listdir(tagged_path) if isfile(join(tagged_path, f))]
    for file in files:
        keywords = get_keywords(file)
        field = get_most_likely(list(categories.keys()), keywords, model)
        categ = get_most_likely(list(categories[field].keys()), keywords, model)
        subcateg = get_most_likely(categories[field][categ], keywords, model)
        print('Finished file ' + file)
        best_category[file] = (field, categ, subcateg)
        print(file + ' belongs to ' + field + ' ---> ' + categ + '--->' + subcateg)
    