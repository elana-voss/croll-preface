"""A chunk's reconciled observations, one line each, for a section writer; notes shortened to fit a token budget."""
import argparse
import os
import sys

import bundle
import outputs
import paths

FOLDER = os.path.join(paths.WORK, 'candidates')


def _line(item, note_chars):
    tags = ', '.join(t for t in item.get('tags') or [] if isinstance(t, str))
    fields = [str(item.get('ref', '')), str(item.get('type', '')), str(item.get('voice', ''))]
    fields += [tags] if tags else []
    fields.append(f"“{item.get('quote', '')}”")
    what = item.get('what') or item.get('term') or ''
    fields += [str(what)] if what else []
    note = str(item.get('note') or '')
    if len(note) > note_chars:
        note = note[:note_chars].rstrip() + ' …'
    fields += [note] if note else []
    return ' | '.join(fields)


def compact(reconciled, budget):
    """Every observation kept; the longest notes are cut first, to one common length, until the text fits."""
    items = [o for o in reconciled.get('observations', []) if isinstance(o, dict)]
    longest = max((len(str(o.get('note') or '')) for o in items), default=0)
    low, high = 0, longest
    while low < high:  # the longest note length that still fits
        mid = (low + high + 1) // 2
        if bundle.tokens('\n'.join(_line(o, mid) for o in items)) <= budget:
            low = mid
        else:
            high = mid - 1
    return '\n'.join(_line(o, low) for o in items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chunks', nargs='+')
    parser.add_argument('--budget', type=int, required=True, help='tokens per chunk')
    args = parser.parse_args()
    for chunk in args.chunks:
        text = compact(outputs.load_json(os.path.join(paths.READINGS, chunk + '.reconciled.json')), args.budget)
        path = os.path.join(FOLDER, chunk + '.txt')
        paths.write(path, text + '\n')
        print(f'{path}: about {bundle.tokens(text):,} tokens')
    return 0


if __name__ == '__main__':
    sys.exit(main())
