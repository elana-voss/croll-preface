"""The word list page: every corrected batch's entries, in alphabetical order, each sense with its marks and the
quoted lines that show it."""
import glob
import os
import sys

import lexicon_lines
import outputs
import paths

PAGE = os.path.join(lexicon_lines.FOLDER, 'lexicon.md')
INTRO = ('# Word List\n\n'
         'The words the Preface uses in a sense of its own or returns to often, in today\'s spelling, with the book\'s '
         'own spellings. Each sense is marked: *plain* where the word means what it ordinarily means, *veiled* where the text '
         'uses it in a covered or second sense; *Stated* where the text itself says the meaning, *Interpreted* where '
         'the meaning is our reading of the lines given, *several* where more than one reading has its basis; and '
         'whose words they are (`CROLL`, the author; `QUOTED: <name>`, a voice he reports; `UNCLEAR`). '
         '*note-only* marks a sense that rests on a margin note alone, *wording-dependent* one that rests on a single '
         'English word of the translator\'s. Each quote is followed by the reference of the line it stands in.\n')


def entry(e):
    """One headword's section of the page."""
    head = e['headword'][0].upper() + e['headword'][1:]
    parts = [f'\n## {head}\n\nThe book spells it: {", ".join(e["spellings"])}\n\n']
    for n, s in enumerate(e['senses'], 1):
        marks = ' · '.join([s['use'], s['reading'], 'voice: ' + s['voice']] + s.get('tags', []))
        parts.append(f'{n}. {s["sense"]} *({marks})*\n')
        parts += [f'   - “{q["quote"]}” [{q["ref"]}]\n' for q in s['evidence']]
    return ''.join(parts)


def render(entries):
    return INTRO + ''.join(entry(e) for e in sorted(entries, key=lambda e: e['headword'].lower()))


def main():
    entries = []
    for name in sorted(glob.glob(os.path.join(lexicon_lines.FOLDER, 'L[0-9][0-9].corrected.json'))):
        entries += outputs.load_json(name)['entries']
    heads = [e['headword'].lower() for e in entries]
    twice = sorted({h for h in heads if heads.count(h) > 1})
    if twice:
        print('headwords in two batches:', ', '.join(twice))
        return 1
    paths.write(PAGE, render(entries))
    print(f'{PAGE}: {len(entries)} entries, {sum(len(e["senses"]) for e in entries)} senses')
    return 0


if __name__ == '__main__':
    sys.exit(main())
