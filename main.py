import re
from os import listdir
from os.path import isfile, join
from nltk.tokenize import sent_tokenize

contentMap  = {}
headerMap   = {}
infoMap     = {}
textMap     = {}
taggedMap   = {}

locations = []
TIME_ROW_REGEX = r'(time|when):'
PLACE_ROW_REGEX = r'(where|place|location):'
INFO_REGEX = r'\w:'
time_regex = r'\b((0?[1-9]|1[012])([:][0-5][0-9])?(\s?[apAP]\.?[Mm])|([01]?[0-9]|2[0-3])([:][0-5][0-9]))\b'

punctuation = ['\.', '?', '!']
separator = 'Abstract:'
pers_title = ['Mr', 'Mr.', 'Mrs', 'Mrs.', 'Ms', 'Ms.', 'Dr', 'Dr.', 'DR', 'DR.', 'Professor', 'Prof', 'Prof.']


def is_info(line):
    if re.match(INFO_REGEX, line) is not None:
        return True
    return False

def get_training_data():
    directories = ['test_tagged', 'training']

    for directory in directories:
        files = [f for f in listdir(directory) if isfile(join(directory, f))]

        # Read and store already known locations and speakers
        sfile = open("Speakers.txt", 'w')
        pfile = open('Locations.txt', 'w')
        for f in files:
            with open(directory + '/' + f, 'r') as file:
                input = file.read()
                location_match = re.search('<location>(.*)</location>', input)
                if location_match is not None:
                    location = location_match.group(1).strip(' ')
                    location = re.sub(r'<.*>', '', location)
                    if location not in locations:
                        locations.append(location)
                    pfile.write(location + '\n')
                speaker_match = re.search('<speaker>(.*)</speaker', input)
                if speaker_match is not None:
                    speaker = speaker_match.group(1).strip(' ')
                    sfile.write(re.sub(r'<.*>', '', speaker) + '\n')

        sfile.close()
        pfile.close()


def read_files():
    my_path = 'test_untagged/'
    only_files = [f for f in listdir(my_path) if isfile(join(my_path, f))]

    # Read the content of all files
    for f in only_files:
        path = my_path + f
        with open(path, 'r') as file:
            contentMap[path] = file.read()
        headerMap[path], infoMap[path], textMap[path] = split_in_parts(contentMap[path])


# Split an email into the actual text and the information lines
def split_in_parts(oontents):
    split_content = contents.split(separator)
    headerMap[path] = split_content[0]
    info = ''
    text = ''
    blocks = split_content[1].split('\n\n')
    for block in blocks:
        if re.match(r'\s', block) is None:
            #print('=============' + block + '' + '=============' + str(is_info(block)))
            if (not (info == '' and text != '')) and (is_info(block.lstrip(' ')) or not any(p not in block for p in punctuation)):
                info += block + '\n\n'
            else:
                text += block + '\n\n'
    return split_content[0], info, text


def tag_header(text):
    low_text = text.lower()

    # Tag the time
    time_match = re.search(TIME_ROW_REGEX, low_text)
    if time_match is not None:
        time_index = time_match.span()[0]
        time_end = time_index + re.search('\n', low_text[time_index:]).span()[0]
        text = text[:time_index] + tag_time(text[time_index:time_end]) + '\n' + text[(time_end + 1):]

    low_text = text.lower()
    # Tag the location and add it to the list
    place_match = re.search(PLACE_ROW_REGEX, low_text)
    if place_match is not None:
        place_index = place_match.span()[0]
        place_end = place_index + re.search('')

    return text


# Tag the sentences of a text
def tag_sent(text):
    sentences = sent_tokenize(text)
    new_content = ''
    for sent in sentences:
        # The built-in sentence tokenizer is not always accurate, so it needs additional validation
        if sent[-1] in '\.?:!\n':
            new_content += '<sentence>' + sent[:-1] + '</sentence>' + sent[-1] + '\n'
    return new_content


def tag_parag(text):
    paragraphs = text.split('\n<sentence>')
    text = paragraphs[0]
    for paragraph in paragraphs:
        text += '\n<paragraph><sentence>' + paragraph + '</paragraph>'
    return text


def tag_location(text):
    for location in locations:
        text = text.replace(location, '<location>' + location + '</location>')
    return text

def tag_time(text):
    new_text = text
    time = re.compile(time_regex)
    tags_length = len('<stime></stime>')
    current = 0

    while current < len(new_text):
        occurance = re.search(time, new_text[current:])
        if occurance is not None:
            start_index = occurance.span()[0]
            end_index = occurance.span()[1]
            if 0 < start_index < 6:
                part1 = new_text[:(current + start_index)] + '<etime>'
                part2 = '</etime>' + new_text[(end_index + current):]
                new_text = part1 + new_text[(current + start_index):(current + end_index)] + part2
            else:
                part1 = new_text[:(current + start_index)] + '<stime>'
                part2 = '</stime>' + new_text[(end_index + current):]
                new_text = part1 + new_text[(current + start_index):(current + end_index)] + part2
            current += end_index + 1 + tags_length
        else:
            break

    return new_text


if __name__ == '__main__':
    get_training_data()

    path = 'test_untagged/347.txt'
    with open(path, 'r') as file:
        contents = file.read()
    header, info, text = split_in_parts(contents)
    #print(tag_sent(text))
    new_content = tag_header(header) + separator + tag_parag(tag_location(tag_time(info + (tag_sent(text)))))
    print(new_content)

