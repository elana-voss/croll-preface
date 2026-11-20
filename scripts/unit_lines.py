"""The book's lines for a unit's pages: what the unit or a page cites first, then the most observed paragraphs of its
sections while they fit; and the readers' observations on those lines, one line each, their quotes cut to locators."""
import argparse
import collections
import glob
import json
import os
import re
import sys

import bundle
import candidates
import outputs
import paths
import preface

FOLDER = os.path.join(paths.WORK, 'pairs')
QUOTE_CHARS = 50  # an observation's quote only locates its line, which the bundle gives in full


def paragraphs_of(book, refs):
    """The paragraphs the references name; a note stands for its paragraph."""
    ids = set()
    for ref in refs:
        for part in re.split(r'[;,]', str(ref)):
            for i in book.expand(part) or []:
                ids.add(book.notes[i]['paragraph'] if i in book.notes else i)
    return ids


def _refs(value):
    if isinstance(value, dict):
        return [r for k, v in value.items() for r in ([v] if k == 'ref' else _refs(v))]
    if isinstance(value, list):
        return [r for v in value for r in _refs(v)]
    return []


def choose(book, cites, observations, budget):
    """`cites` is a unit entry or a list of references; the result is never smaller than what they cite."""
    chosen = paragraphs_of(book, _refs(cites) if isinstance(cites, dict) else cites)
    sections = {book.section_of(p) for p in chosen}
    counts = collections.Counter(p for o in observations for p in paragraphs_of(book, [o.get('ref', '')]))
    rest = [p for s in sections for p in book.paragraph_ids(s) if p not in chosen and counts[p]]
    for p in sorted(rest, key=lambda p: -counts[p]):  # sorted() is stable: ties keep the book's order
        if bundle.tokens(bundle.render(book, chosen | {p})) <= budget:
            chosen.add(p)
    return chosen


def locator(observation):
    quote = str(observation.get('quote', ''))
    if len(quote) <= QUOTE_CHARS:
        return observation
    return dict(observation, quote=quote[:QUOTE_CHARS].rstrip() + ' …')


def observations():
    return [o for path in sorted(glob.glob(os.path.join(paths.READINGS, '*.reconciled.json')))
            for o in outputs.load_json(path).get('observations', []) if isinstance(o, dict)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', help='output name: <name>.ids.txt and <name>.candidates.txt in work/pairs')
    parser.add_argument('--unit', help='a unit id of work/division/settled.json')
    parser.add_argument('--page', help='a page whose references are cited')
    parser.add_argument('--budget', type=int, required=True, help='tokens for the lines')
    parser.add_argument('--candidates', type=int, default=0, help='tokens for the observations; 0 writes none')
    args = parser.parse_args()
    book, seen = preface.load(), observations()
    if args.unit:
        units = outputs.load_json(os.path.join(paths.WORK, 'division', 'settled.json'))['units']
        cites = next(u for u in units if u.get('id') == args.unit)
        paths.write(os.path.join(FOLDER, args.name + '.unit.json'), json.dumps(cites, indent=1, ensure_ascii=False) + '\n')
    else:
        cites = outputs.REF_BRACKET.findall(outputs.read(args.page))
    ids = choose(book, cites, seen, args.budget)
    paths.write(os.path.join(FOLDER, args.name + '.ids.txt'), ' '.join(p for p in book.paragraphs if p in ids) + '\n')
    if args.candidates:
        mine = [locator(o) for o in seen if paragraphs_of(book, [o.get('ref', '')]) & ids]
        paths.write(os.path.join(FOLDER, args.name + '.candidates.txt'),
                    candidates.compact({'observations': mine}, args.candidates) + '\n')
    print(f'{args.name}: {len(ids)} paragraphs, about {bundle.tokens(bundle.render(book, ids)):,} tokens of lines')
    return 0


if __name__ == '__main__':
    sys.exit(main())
