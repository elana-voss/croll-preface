"""Decide every word broken at a line end: join the halves or keep a hyphen.

The Preface itself is the evidence: a joined form printed unbroken elsewhere means join,
a hyphenated form printed within a line elsewhere (and more often) means keep the hyphen.
Without evidence the halves are joined, the printer's usual practice; where both halves
are words of their own the row says so ('both-words'), as the least certain decisions.
"""
import collections
import re

import textnorm
from tei import EOL, EOL_PLAIN, ITALIC_OFF, ITALIC_ON

BREAK = re.compile(f'[{EOL}{EOL_PLAIN}]')
TOKEN = re.compile(f'(?:[^\\W_]|[{EOL}{EOL_PLAIN}])+')
COMPOUND = re.compile(r'([^\W_]+)-([^\W_]+)')
LEFT, RIGHT = re.compile(r'[^\W_]*$'), re.compile(r'[^\W_]*')


def _plain(text):
    return text.replace(ITALIC_ON, '').replace(ITALIC_OFF, '')


def decide(texts):
    """One row per break, in text order: {'text': index, 'left', 'right', 'decision', 'basis'}."""
    texts = [_plain(t) for t in texts]
    unbroken = collections.Counter(textnorm.key(m.group()) for t in texts for m in TOKEN.finditer(t)
                                   if not BREAK.search(m.group()))
    hyphenated = collections.Counter((textnorm.key(a), textnorm.key(b))
                                     for t in texts for a, b in COMPOUND.findall(t))
    rows = []
    for index, text in enumerate(texts):
        for match in BREAK.finditer(text):
            left = LEFT.search(text, 0, match.start()).group()
            right = RIGHT.match(text, match.end()).group()
            pair = textnorm.key(left), textnorm.key(right)
            decision, basis = 'join', 'default'
            if match.group() == EOL_PLAIN:
                basis = 'unhyphenated'
            elif not left or not right:
                basis = 'edge'
            elif hyphenated[pair] > unbroken[''.join(pair)]:
                decision, basis = 'hyphen', 'hyphenated-elsewhere'
            elif unbroken[''.join(pair)]:
                basis = 'joined-elsewhere'
            elif unbroken[pair[0]] and unbroken[pair[1]]:
                basis = 'both-words'
            rows.append({'text': index, 'left': left, 'right': right, 'decision': decision, 'basis': basis})
    return rows
