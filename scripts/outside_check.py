"""List the words of an output found neither in the Preface nor in plain English, for its corrector."""
import argparse
import collections
import re
import sys

import outputs
import preface
import prompt_check
import textnorm

LABEL_KEYS = {'type', 'voice', 'ref', 'tags', 'from', 'sections_read', 'end_marker', 'verdict', 'kind'}


def text_of(data):
    """The free text of a JSON value; keys and fixed labels left out."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        data = [value for key, value in data.items() if key not in LABEL_KEYS]
    if isinstance(data, list):
        return ' '.join(part for part in map(text_of, data) if part)
    return ''


def prose(text):
    """A page's text without its links' targets."""
    return re.sub(r'\]\([^)]*\)', ']', text)


def outside(book, data, plain):
    def stem(word):
        return re.split(r"['’]", word)[0]  # a possessive is listed by its stem
    book_words = book.words()
    known = set(book_words) | {stem(w) for w in book_words}
    stems = (stem(w) for w in textnorm.words(text_of(data)))
    found = (w for w in stems if w.isalpha() and w not in known and w not in plain)
    return dict(sorted(collections.Counter(found).items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path')
    args = parser.parse_args()
    book = preface.load()
    if outputs.is_json(args.path):
        data = outputs.load_json(args.path)
    else:
        data = outputs.REF_BRACKET.sub(' ', prose(outputs.page_body(outputs.read(args.path))))
    found = outside(book, data, prompt_check.load(book).plain)
    outputs.report([f'{word} {count}' for word, count in found.items()], 'no outside words')
    return 0  # a list for the corrector to judge, not a failure


if __name__ == '__main__':
    sys.exit(main())
