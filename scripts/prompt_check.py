"""Prompts carry no word of the Preface and no uncommon word, unless reviewed as ordinary language.

This keeps the book's own vocabulary, and any other book's, out of what steers the agents.
"""
import argparse
import os
import sys
from dataclasses import dataclass

import outputs
import paths
import preface
import textnorm

REVIEWED = os.path.join(paths.PROMPTS, 'reviewed_words.txt')


@dataclass
class Lists:
    plain: set  # plain English
    reviewed: set  # looked at by hand: ordinary language or a format name, not a term of any subject
    book_words: set


def flagged(text, lists):
    found = set()
    for word in textnorm.words(text):
        word = word.split("'")[0].split('’')[0]
        if word.isalpha() and word not in lists.reviewed and (word not in lists.plain or word in lists.book_words):
            found.add(word)
    return sorted(found)


def problems(prompt_paths, lists):
    return [f'{os.path.basename(p)}: {word}' for p in prompt_paths for word in flagged(outputs.read(p), lists)]


def _read_words(path):
    rows = (row.strip() for row in outputs.read(path).splitlines()) if os.path.exists(path) else []
    return {row for row in rows if row and not row.startswith('#')}


def load(book):
    return Lists(_read_words(paths.PLAIN_ENGLISH), _read_words(REVIEWED), book.words())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prompts', nargs='+')
    args = parser.parse_args()
    return outputs.report(problems(args.prompts, load(preface.load())), 'prompts pass')


if __name__ == '__main__':
    sys.exit(main())
