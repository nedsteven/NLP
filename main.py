import re
from os import listdir
from os.path import isfile, join
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag

contentMap  = {}
headerMap   = {}
infoMap     = {}
textMap     = {}

locationMap = {}
stimeMap = {}
etimeMap = {}
speakerMap = {}

locations = []
speakers = []

TIME_ROW_REGEX = r'((time)|(when)):'
PLACE_ROW_REGEX = r'((where)|(place)|(location)):'
SPEAKER_ROW_REGEX = r'((who)|(speaker)|(name)):'
INFO_REGEX = r'\w:'
time_regex = r'\b(?<!>)((0?[1-9]|1[012])([:][0-5][0-9])?(\s?[apAP]\.?[Mm])|([01]?[0-9]|2[0-3])([:][0-5][0-9]))\b'
speaker_regex = r'((M[Rr])|(M[Ss])|(M[RrSs])|(D[rR])|(P[RrOoFf])|(Professor))(\.)? '

punctuation = ['\.\?\!']
separator = 'Abstract:'


def get_training_data():
    directories = ['training']

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
                    location = location_match.group(1).strip()
                    location = re.sub(r'<.*>', '', location)
                    if location not in locations:
                        locations.append(location)
                    pfile.write(location + '\n')
                speaker_match = re.search('<speaker>(.*)</speaker', input)
                if speaker_match is not None:
                    speaker = speaker_match.group(1).strip()
                    sfile.write(re.sub(r'<.*>', '', speaker) + '\n')
                    if speaker not in speakers:
                        speakers.append(speaker)
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
            contentMap[path] = file.read()
        
        tmp = contentMap[path].split(separator)
        headerMap[path] = tmp[0]
        if len(tmp) > 1:
            textMap[path] = tmp[1]
        else:
            textMap[path] = ''

        # Get relevant information
            # stime, etime, location, speaker = get_info(path)
            # tag_info(path, stime, etime, location, speaker) 

        if path in list(textMap.keys()):
            textMap[path] = tag_parag_and_sent(path)
        else:
            textMap[path] = ''
        contentMap[path] = headerMap[path] + separator + '\n' + textMap[path]
        
        tag_speaker(path)
        tag_location(path)
        tag_time(path)

        # Create files and print the results
        file = open(result_path + f, 'w')
        file.write(contentMap[path])
        file.close()


def is_parag(block):
    check = False
    tokens = word_tokenize(block)
    for token, pos in pos_tag(tokens):
        if pos[0] == 'V':
            check = True
            break
        if "." in token:
            return False
    if len(tokens) > 0 and not tokens[0][0].isupper():
        check = False
    return check


def tag_parag_and_sent(path):
    blocks = re.split(r'\n\s', textMap[path])
    new_content = ''
    for block in blocks:
        if (is_parag(block)):
            sents = sent_tokenize(block)
            new_block = ''
            for i in range(len(sents)):
                sents[i] = sents[i]
                if sents[i][0].isupper() and sents[i][0].isalpha():
                    if sents[i][-1] in '.:':
                        sents[i] = '<sentence>' + sents[i][:-1] + '</sentence>' + sents[i][-1]
                    else:
                        sents[i] = '<sentence>' + sents[i] + '</sentence>'
            new_block = '<paragraph>' + ' '.join(sents) + '</paragraph>' + '\n\n'
            #print(new_block + '\n================ ' + str(block in contentMap[path]) + ' ============')
            new_content = ''.join([new_content, new_block])
            #contentMap[path].replace(block, new_block)
            #print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n' + contentMap[path] + '\n')
        else:
            new_content = new_content + block + '\r\n'
    return new_content
            

def tag_speaker(path):
    match = re.search(SPEAKER_ROW_REGEX, contentMap[path].lower())
    if match is not None:
        speaker_row = contentMap[path][match.span()[0]:].split('\n')[0]
        speaker = re.split(r',|\-|( [a-z])|\(|/', speaker_row[(speaker_row.find(':') + 1):])[0].strip()
        contentMap[path] = contentMap[path].replace(speaker, '<speaker>' + speaker + '</speaker>')
        speakers.append(speaker)
    else:
        match = re.search(speaker_regex, contentMap[path])
        if match is not None:
            title = match.group(0)
            name_start = match.span()[1]
            name = ''
            words = re.split(r' |,|:|\'', contentMap[path][name_start:], 5)
            for i in range(len(words) - 1):
                if len(words[i]) > 0 and words[i][0].isalpha() and words[i][0].isupper():
                    name =  name + words[i] + ' '
                    if words[i][-1] == '.' and len(words[i]) > 3:
                        break
                else:
                    break
            speaker = (title + name).split('\n')[0].strip()
            if (len(speaker.split()) > 1):
                contentMap[path] = contentMap[path].replace(speaker, '<speaker>' + speaker + '</speaker>')
                speakers.append(speaker)
        else:
            found = []
            for speaker in speakers:
                if speaker in contentMap[path]:
                    found.append(speaker)
            for idx in range(len(found) - 1):
                for i in range(idx + 1, len(found)):
                    if found[idx] in found[i]:
                        found.remove(found[i])
                        i = i - 1
            for speaker in found:
                contentMap[path] = contentMap[path].replace(speaker, '<speaker>' + speaker + '</speaker>')


# Tag the location based on the training data offering examples
def tag_location(path):
    match = re.search(PLACE_ROW_REGEX, contentMap[path].lower())
    if match is not None:
        location_row = contentMap[path][match.span()[0]:].split('\n')[0]
        location = location_row[(location_row.find(':') + 1):].strip()
        locations.append(location)
        contentMap[path] = contentMap[path].replace(location, '<location>' + location + '</location>')
    else:
        found = []
        for location in locations:
            if location in contentMap[path]:
                found.append(location)
        found2 = found
        doubles = []
        for location in found:
            for location2 in found2:
                if location in location2 and location != location2:
                    doubles.append(location)
        for location in doubles:
            if location in found:
                found.remove(location)
        for location in found:
            contentMap[path] = contentMap[path].replace(location, '<location>' + location + '</location>')


def tag_time(path):
    new_text = contentMap[path]
    tags_length = len('<stime></stime>')
    current = 0

    while current < len(new_text):
        match = re.search(time_regex, new_text[current:])
        if match is not None:
            start_index = match.span()[0]
            end_index = match.span()[1]
            time = match.group(1)
            if start_index < 6:
                part1 = new_text[:(current + start_index)] + '<etime>'
                part2 = '</etime>' + new_text[(end_index + current):]
                new_text = part1 + new_text[(current + start_index):(current + end_index)] + part2
            else:
                postedby = re.search('PostedBy:(.*)\n', headerMap[path])
                if postedby is not None:
                    print(path + ' ' + str(time in postedby.group(1)))
                if postedby is None or time not in postedby.group(1): 
                    part1 = new_text[:(current + start_index)] + '<stime>'
                    part2 = '</stime>' + new_text[(end_index + current):]
                    new_text = part1 + new_text[(current + start_index):(current + end_index)] + part2
            current += end_index + tags_length
        else:
            break
    contentMap[path] = new_text


if __name__ == '__main__':

    get_training_data()
    #path = 'untagged/301.txt'
    read_files()
    #with open('untagged/301.txt', 'r') as f:
     #   contentMap[path] = f.read()
    #print(contentMap[path])
    
