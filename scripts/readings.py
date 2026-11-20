"""What the reconciled readings give the later steps: the second-reader trial, markings, voices, headwords.

Files: work/readings/<chunk>.A.json and .B.json (readers, `items` numbered `n`), <chunk>.reconciled.json.
"""
import json
import os
import re
import sys

import outputs
import paths
import preface
import textnorm


def _sources(value):
    """A `from` field as a list of text ids, whatever form the agent wrote it in."""
    if isinstance(value, list):
        return [str(s) for s in value]
    return [] if value is None else [str(value)]


def _dicts(data, key):
    """The dictionaries of a list field; anything else an agent wrote there is left out."""
    value = data.get(key) if isinstance(data, dict) else None
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def _check(chunk, a, b, reconciled):
    """Every reader item is kept or dropped, once; every source is a reader item. Returns problems, known ids."""
    problems, known = [], set()
    for letter, reader in (('A', a), ('B', b)):
        for item in (reader.get('items', []) if isinstance(reader, dict) else []):
            if isinstance(item, dict) and isinstance(item.get('n'), int):
                known.add(f'{letter}{item["n"]}')
            else:
                problems.append(f'{chunk}: reader {letter} item without a number')
    observations = _dicts(reconciled, 'observations')
    kept = [s for o in observations for s in _sources(o.get('from'))]
    dropped = [s for d in _dicts(reconciled, 'dropped') for s in _sources(d.get('from'))]
    problems += [f'{chunk}: {s} is no reader item' for s in dict.fromkeys(kept + dropped) if s not in known]
    problems += [f'{chunk}: {s} both kept and dropped' for s in sorted(known & set(kept) & set(dropped), key=_order)]
    problems += [f'{chunk}: observation {i} has no source' for i, o in enumerate(observations, 1)
                 if not known & set(_sources(o.get('from')))]
    problems += [f'{chunk}: {s} neither kept nor dropped' for s in sorted(known - set(kept + dropped), key=_order)]
    return problems, known


def _order(source):
    return source[0], int(source[1:])


def trial(rows):
    """rows: (chunk, reader A, reader B, reconciled). The share of observations only one reader found."""
    counts = {'observations': 0, 'one_reader': 0, 'only_A': 0, 'only_B': 0}
    problems = []
    for chunk, a, b, reconciled in rows:
        found, known = _check(chunk, a, b, reconciled)
        problems += found
        for observation in _dicts(reconciled, 'observations'):
            readers = {s[0] for s in _sources(observation.get('from')) if s in known}
            if not readers:
                continue  # reported by _check
            counts['observations'] += 1
            if len(readers) == 1:
                counts['one_reader'] += 1
                counts['only_' + readers.pop()] += 1
    share = round(counts['one_reader'] / counts['observations'], 3) if counts['observations'] else 0
    keys = ['observations', 'one_reader', 'share', 'only_A', 'only_B']
    return {k: share if k == 'share' else counts[k] for k in keys}, problems


def _position(book, ref):
    first = outputs.refs_in(ref)[0] if outputs.refs_in(ref) else ''
    ids = book.expand(first) or []
    return book.order.index(ids[0]) if ids else len(book.order)


def markings(book, rows):
    found = [{'chunk': chunk, 'ref': o['ref'], 'quote': o.get('quote', ''), 'what': o.get('what', ''),
              'voice': o.get('voice', ''), 'tags': o.get('tags', [])}
             for chunk, reconciled in rows for o in _dicts(reconciled, 'observations')
             if o.get('type') == 'marking' and isinstance(o.get('ref'), str)]
    return sorted(found, key=lambda m: _position(book, m['ref']))


def voices(rows):
    return [{'chunk': chunk, **span} for chunk, reconciled in rows for span in _dicts(reconciled, 'voices')]


def _key(term):
    return ' '.join(textnorm.words(term))


def _spelling(text):
    return re.sub(r'^\W+|\W+$', '', textnorm.printed(text))


def headwords(book, rows):
    """Candidates: every term the readers named and every italic stretch of the Preface, with where each stands."""
    entries = {}

    def entry(spelling):
        key = _key(spelling)
        if key and key not in entries:
            entries[key] = {'key': key, 'spellings': [], 'read_at': [], 'italic_at': [], 'occurs_at': []}
        return entries.get(key)

    def add(row, field, value):
        if value not in row[field]:
            row[field].append(value)

    for _, reconciled in rows:
        for o in _dicts(reconciled, 'observations'):
            if isinstance(o.get('term'), str) and isinstance(o.get('ref'), str) and entry(o['term']):
                add(entries[_key(o['term'])], 'spellings', _spelling(o['term']))
                for ref in outputs.refs_in(o['ref']):
                    add(entries[_key(o['term'])], 'read_at', ref)
    for italic in book.italics:
        row = entry(italic['text'])
        if row:
            add(row, 'spellings', _spelling(italic['text']))
            add(row, 'italic_at', italic['in'])
    for key, row in entries.items():
        whole = re.compile(r'(?<!\S)' + re.escape(key) + r'(?!\S)')
        row['occurs_at'] = [i for i in book.order if whole.search(' '.join(textnorm.words(book.texts[i])))]
    return sorted(entries.values(), key=lambda r: (not r['read_at'], -len(r['occurs_at']), r['key']))


def _load_rows(folder):
    names = sorted(f[:-len('.reconciled.json')] for f in os.listdir(folder) if f.endswith('.reconciled.json'))
    rows, problems = [], []
    for chunk in names:
        try:
            rows.append((chunk, *(outputs.load_json(os.path.join(folder, f'{chunk}.{kind}.json'))
                                  for kind in ('A', 'B', 'reconciled'))))
        except (OSError, ValueError) as error:
            problems.append(f'{chunk}: {error}')
    return rows, problems


def _write(name, data):
    paths.write(os.path.join(paths.WORK, name), json.dumps(data, indent=1, ensure_ascii=False) + '\n')


def main():
    book = preface.load()
    rows, unreadable = _load_rows(paths.READINGS)
    figure, problems = trial(rows)
    problems = unreadable + problems
    reconciled = [(chunk, r) for chunk, _, _, r in rows]
    _write('markings.json', markings(book, reconciled))
    _write('voices.json', voices(reconciled))
    _write('headwords.json', headwords(book, reconciled))
    print(f'second-reader trial over {len(rows)} chunks: {figure}')
    return outputs.report(problems, 'every reader item kept or dropped')


if __name__ == '__main__':
    sys.exit(main())
