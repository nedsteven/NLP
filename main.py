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
SPEAKER_ROW_REGEX = r'(who|by|speaker|name):'
INFO_REGEX = r'\w:'
time_regex = r'\b(?<!>)((0?[1-9]|1[012])([:][0-5][0-9])?(\s?[apAP]\.?[Mm])|([01]?[0-9]|2[0-3])([:][0-5][0-9]))\b'

punctuation = ['\.', '?', '!']
separator = 'Abstract:\n'
pers_title = ['Mr', 'Mr.', 'Mrs', 'Mrs.', 'Ms', 'Ms.', 'Dr', 'Dr.', 'DR', 'DR.', 'Professor', 'Prof', 'Prof.']


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
    my_path = 'untagged/'
    result_path = 'tagged/'
    only_files = [f for f in listdir(my_path) if isfile(join(my_path, f))]

    # Read the content of all files
    for f in only_files:
        path = my_path + f
        with open(path, 'r') as file:
            headerMap[path], infoMap[path], textMap[path] = split_in_parts(file.read())

        # Get relevant information
        info = get_info(path)
        stime = str(info[0])
        etime = str(info[1])
        location = str(info[2])
        speaker = str(info[3])
        tag_info(path, stime, etime, location, speaker) 

        # Create files and print the results
        file = open(result_path + f, 'w')
        new_content = headerMap[path] + separator + '\n' + infoMap[path] + tag_parag(tag_sent(textMap[path]))
        file.write(new_content)
        file.close()


# Go through the email and tag the known data from the header
def tag_info(path, stime, etime, location, speaker):
    if stime != '':
        infoMap[path].replace(stime, '<stime>' + stime + '</stime>')
        textMap[path].replace(stime, '<stime>' + stime + '</stime>')
        if (etime != ''):
            infoMap[path].replace(etime, '<etime>' + etime + '</etime>')
            textMap[path].replace(etime, '<etime>' + etime + '</etime>')
        else:
            infoMap[path] = tag_time(infoMap[path])
            textMap[path] = tag_time(textMap[path])
    if speaker != '':
        infoMap[path].replace(speaker, '<speaker>' + speaker + '</speaker>')
        textMap[path].replace(speaker, '<stime>' + speaker + '</speaker>')
    if location != '':
        infoMap[path].replace(location, '<location>' + location + '</location>')
        textMap[path].replace(stime, '<location>' + location + '</location>')
    else:
        infoMap[path] = tag_location(infoMap[path])
        textMap[path] = tag_location(textMap[path])


# Split an email into the actual text and the information lines
def split_in_parts(contents):
    split_content = contents.split(separator)
    info = ''
    text = ''
    if len(split_content) > 1:
        blocks = split_content[1].split('\n')
        for block in blocks:
            if re.match(r'\s', block) is None:
                #print('=============' + block + '' + '=============' + str(is_info(block)))
                if (not (info == '' and text != '')) and (is_info(block.lstrip(' ')) or not any(p not in block for p in punctuation)):
                    info += block + '\n'
                else:
                    text += block + '\n'
    return split_content[0], info, text


# This function returns true if the line i
def is_info(line):
    if re.match(INFO_REGEX, line) is not None:
        return True
    return False


# Retrieve the relevant information from the header
def get_info(path):
    lines = (headerMap[path] + '\n' + infoMap[path]).split('\n')

    time_row = ''
    place_row = ''
    speaker_row = ''
    start_time = ''
    end_time = ''
    speaker = ''
    location = ''

    for line in lines:
        if re.match(TIME_ROW_REGEX, line.lower()) is not None:
            time_row = line
        elif re.match(PLACE_ROW_REGEX, line.lower()) is not None:
            place_row = line
        elif re.match(SPEAKER_ROW_REGEX, line.lower()) is not None:
            speaker_row = line

    # Tag the time
    if time_row != '':
        times = re.findall(time_regex, time_row)
        start_time = times[0]
        headerMap[path].replace(start_time, '<stime>' + start_time + '</stime>')
        if (len(times) > 1):
            end_time = times[1]
            headerMap[path].replace(end_time, '<etime>' + end_time + '</etime>')

    # Tag the location and add it to the list
    if place_row != '':
        location = text[text.find(':'):].strip('\s\t')
    
    # Tag the speaker, if they are specified in the header
    if speaker_row != '':
        speaker = text[text.find(':'):].strip('\s\t')

    return start_time, end_time, location, speaker


# Tag the sentences of a text
def tag_sent(text):
    sentences = sent_tokenize(text)
    new_content = ''
    for sent in sentences:
        # The built-in sentence tokenizer is not always accurate, so it needs additional validation
        if sent[-1] in '\.?:!\n':
            if not sent[0].isalnum():
                real_sent = re.search(r'\n\w', sent)
                if real_sent is not None:
                    new_content += sent[:real_sent.span()[0]]
                    sent = sent[real_sent.span()[0]:]
            new_content += '<sentence>' + sent[:-1] + '</sentence>' + sent[-1]
    return new_content


# Tag paragraphs, based on the fact that they are supposed to start with a sentence
# and have an empty line before them
def tag_parag(text):
    paragraphs = text.split('\n\n')
    text = paragraphs[0]
    for paragraph in paragraphs:
        if re.match(r'<sentence>', paragraph):
            text += '<paragraph><sentence>' + paragraph + '</paragraph>\n\n'
        else:
            text += paragraph + '\n\n'
    return text


# Tag the location based on the training data offering examples
def tag_location(text):
    found = []
    for location in locations:
        if location in text:
            found.append(location)
    for idx in range(len(found) - 1):
        for i in range(idx + 1, len(found)):
            if found[idx] in found[i]:
                found.remove(found[i])
                i = i - 1
    for location in found:
        text = text.replace(location, '<location>' + location + '</location>')
    return text


def tag_time(text):
    new_text = text
    tags_length = len('<stime></stime>')
    current = 0

    while current < len(new_text):
        occurance = re.search(time_regex, new_text[current:])
        if occurance is not None:
            start_index = occurance.span()[0]
            end_index = occurance.span()[1]
            if start_index < 6:
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
    read_files()
    #path = 'test_untagged/347.txt'
    #with open(path, 'r') as file:
     #   contents = file.read()
    #header, info, text = split_in_parts(contents)
    #print(tag_sent(text))
    #new_content = tag_header(header) + separator + tag_parag(tag_location(tag_time(info + (tag_sent(text)))))
    # print(new_content)


