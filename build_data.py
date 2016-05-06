import json
import nltk.data

from collections import Counter
from itertools import repeat, chain
from nltk import word_tokenize
from nltk.collocations import TrigramAssocMeasures, TrigramCollocationFinder

# Declaring variables
input_file = './sample_conversations.json'
output_file = './brute_force.json'
filtered_output_file = './trigram_filtered.json'


def remove_dupes_with_ordering(seq):
    '''
    Helper method to remove duplicate entires in a list while
    maintaining the order.
    '''
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def read_json(input_file):
    '''
    Helper method to wrap opening and reading a given file.
    '''

    with open(input_file) as file:
        data = json.load(file)

    return data


def write_json(output_file, data):
    '''
    Helper method to write processed data to json.
    '''

    with open(output_file, 'w') as out_file:
        json.dump(data, out_file)


def get_sentences(data):
    '''
    Parses json data into sentences.

    Assumes that the json in 'input_file' is formated as follows:

    NumTextMessages
    Issues
    --->IssueId
    --->CompanyGroupId
    --->Messages
        --->IsFromCustomer
        --->Text
    '''

    # Initialize our sentence parser
    sentence_parser = nltk.data.load('tokenizers/punkt/english.pickle')

    # Pull out the messages that will go into our corpus
    rep_messages = [
        i['Text']
        for arr in data['Issues']
        for i in arr['Messages']
        if not i['IsFromCustomer']
    ]

    # Grab all of the existing sentences
    sentences = [
        sen
        for msg in rep_messages
        for sen in sentence_parser.tokenize(msg.strip())
    ]

    return sentences


def generate_basic_suggestions(sentences):
    '''
    Initial brute force processing of data into suggestions.

    Takes an array of sentences and produces a dict whose keys
    are any existing partials of the sentences that exist in the
    corpus and whose values are a list of phrases that start with
    that key.

    After these lists are generated, their values are sorted so that
    the most common are first, then reduced so that only unique values
    remain.
    '''
    suggestion_dict = {}

    for sentence in sentences:
        for i, char in enumerate(sentence, start=1):
            key = sentence[:i].lower()
            if suggestion_dict.get(key):
                suggestion_dict[key].append(sentence)
            else:
                suggestion_dict[key] = [sentence]

    # Sort responses by number of occurances and remove duplicates
    for k, v in suggestion_dict.iteritems():
        v = list(
            chain.from_iterable(
                repeat(i, c) for i, c in Counter(v).most_common()
            ))
        v = remove_dupes_with_ordering(v)
        suggestion_dict[k] = v

    return suggestion_dict


def get_trigrams(sentences, freq_filter):
    '''
    Method to parse corpus into trigrams, then filter to include
    only those that occur more than 10 times.
    '''
    # Initialize trigram utils
    trigram_measures = TrigramAssocMeasures()
    trigram_finder = TrigramCollocationFinder.from_words(
        word_tokenize(" ".join(sentences).lower()))

    # Filter trigrams by frequency to reduce pmi pollution
    trigram_finder.apply_freq_filter(freq_filter)
    # Generate pmi ranked set of trigrams for sorting
    scored = trigram_finder.score_ngrams(trigram_measures.pmi)

    return sorted(trigram for trigram, score in scored)


def filter_sentences_by_trigrams(sentences, trigrams):
    '''
    Filter sentences in the corpus to include only those that
    contain at least one of the trigrams passed in.
    '''
    filtered_sentences = []
    for s in sentences:
        for t in trigrams:
            substring = " ".join(t)
            if substring in s:
                filtered_sentences.append(s)
                break

    return filtered_sentences


if __name__ == "__main__":
    raw_data = read_json(input_file)
    sentences = get_sentences(raw_data)
    trigrams = get_trigrams(sentences, 10)
    filtered_sentences = filter_sentences_by_trigrams(sentences, trigrams)
    suggestions = generate_basic_suggestions(sentences)
    filtered_suggestions = generate_basic_suggestions(filtered_sentences)
    write_json(output_file, suggestions)
    write_json(filtered_output_file, filtered_suggestions)
