"""Word-list batches: the headwords read at two or more places, their variant spellings joined; for each batch the
book's lines where its headwords stand (a spread of the places the readers named, then of the others) and the
readers' observations on its headwords, one line each, their quotes cut to locators."""
import argparse
import json
import os
import sys

import bundle
import candidates
import outputs
import paths
import preface
import readings
import unit_lines

FOLDER = os.path.join(paths.WORK, 'lexicon')
READ_LINES = 8  # places the readers named, per headword
OTHER_LINES = 2  # further places the word stands, per headword


def spread(items, n):
    """At most n items, evenly spaced, the first and last kept, in their order."""
    if len(items) <= n:
        return list(items)
    if n == 1:
        return [items[0]]
    return [items[round(i * (len(items) - 1) / (n - 1))] for i in range(n)]


def groups(rows, merges, min_read):
    """Rows joined by the merge lists (each a list of keys), kept where the readers named them at min_read places."""
    by_key = {r['key']: r for r in rows}
    joined, seen = [], set()
    for keys in merges + [[r['key']] for r in rows]:
        keys = [k for k in keys if k in by_key and k not in seen]
        if not keys:
            continue
        seen.update(keys)
        group = {'keys': keys, 'spellings': [], 'read_at': [], 'occurs_at': []}
        for key in keys:
            for field in ('spellings', 'read_at', 'occurs_at'):
                group[field] += [v for v in by_key[key][field] if v not in group[field]]
        joined.append(group)
    return [g for g in joined if len(g['read_at']) >= min_read]


def lines_of(book, group):
    others = [i for i in group['occurs_at'] if i not in group['read_at']]
    return unit_lines.paragraphs_of(book, spread(group['read_at'], READ_LINES) + spread(others, OTHER_LINES))


def batches(book, chosen, budget):
    """Headwords in the order they are first read, gathered while their lines fit the budget; one alone may exceed."""
    first = {i: n for n, i in enumerate(book.order)}
    result, ids = [], set()
    for group in sorted(chosen, key=lambda g: min(first.get(r, len(first)) for r in g['read_at'])):
        mine = lines_of(book, group)
        if result and bundle.tokens(bundle.render(book, ids | mine)) <= budget:
            result[-1].append(group)
            ids |= mine
        else:
            result.append([group])
            ids = set(mine)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budget', type=int, required=True, help="tokens of lines per batch")
    parser.add_argument('--candidates', type=int, required=True, help='tokens of observations per batch')
    args = parser.parse_args()
    book = preface.load()
    rows = outputs.load_json(os.path.join(paths.WORK, 'headwords.json'))
    merges = outputs.load_json(os.path.join(FOLDER, 'merges.json'))
    seen = unit_lines.observations()
    for n, batch in enumerate(batches(book, groups(rows, merges, 2), args.budget), 1):
        name, keys = f'L{n:02d}', {k for g in batch for k in g['keys']}
        ids = set().union(*(lines_of(book, g) for g in batch))
        mine = [unit_lines.locator(o) for o in seen
                if isinstance(o.get('term'), str) and readings.key(o['term']) in keys]
        stem = os.path.join(FOLDER, name)
        paths.write(stem + '.headwords.txt', ''.join(' / '.join(g['spellings']) + '\n' for g in batch))
        paths.write(stem + '.ids.txt', ' '.join(p for p in book.paragraphs if p in ids) + '\n')
        paths.write(stem + '.candidates.txt', candidates.compact({'observations': mine}, args.candidates) + '\n')
        print(f'{name}: {len(batch)} headwords, {len(ids)} paragraphs, '
              f'about {bundle.tokens(bundle.render(book, ids)):,} tokens of lines, {len(mine)} observations')
    return 0


if __name__ == '__main__':
    sys.exit(main())
