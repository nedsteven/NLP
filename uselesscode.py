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
                if (not (info == '' and text != '')) and (is_info(block.lstrip(' ')) or not any(p not in block for p in punctuation)):
                    info += block + '\n'
                else:
                    text += block + '\n'
            else:
                info += block + '\n'
    return split_content[0], info, text


# This function returns true if the line i
def is_info(line):
    if re.match(INFO_REGEX, line) is not None:
        return True
    return False


# Retrieve the relevant information from the header
def get_info(path):
    text = headerMap[path] + '\n' + infoMap[path]
    lines = text.split('\n')

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
        start_time = times[0][0]
        headerMap[path].replace(start_time, '<stime>' + start_time + '</stime>')
        if (len(times) > 1):
            end_time = times[1][0]
            headerMap[path].replace(end_time, '<etime>' + end_time + '</etime>')

    # Tag the location and add it to the list
    if place_row != '':
        location = place_row[(place_row.find(':') + 1):].strip()
        headerMap[path].replace(location, '<location>' + location + '</location>')
    
    # Tag the speaker, if they are specified in the header
    if speaker_row != '':
        speaker = speaker_row[(speaker_row.find(':') + 1):].strip().split(',')[0]
        headerMap[path].replace(speaker, '<speaker>' + speaker + '</speaker>')

    return start_time, end_time, location, speaker




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

