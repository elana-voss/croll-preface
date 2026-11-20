"""Write the Preface's text files and its tables from the TEI source.

text/<SECTION>.txt   one line per paragraph, `<id> <text>`, each followed by its notes, `<N…> <text>`
text/preface.json    sections, paragraphs, notes, gaps, italics, chunks, with word counts
text/joins.json      the breaks kept as hyphens and the least certain joins, for checking
"""
import hashlib
import json
import os
import re
import sys

import chunks
import joins
import paths
import tei
import textnorm

MARKER = re.compile(f'[{tei.EOL}{tei.EOL_PLAIN}]|{tei.GAP}(\\d+){tei.GAP}|{tei.NOTE}(\\d+){tei.NOTE}'
                    f'|{tei.NUMERAL}([IVXLC]+){tei.NUMERAL}')
LAYOUT_AT_BREAK = re.compile(rf'\s*([{tei.EOL}{tei.EOL_PLAIN}])\s*')
ITALIC = re.compile(f'{tei.ITALIC_ON}(.*?){tei.ITALIC_OFF}', re.S)
REFERENCE_WORDS = {'de', 'in', 'lib', 'cap', 'chap', 'tract', 'fol', 'sol', 'vid', 'see', 'c', 'v'}
REFERENCE_SIGNS = {'lib', 'cap', 'chap', 'tract', 'fol', 'sol'}


def note_id(index):
    return f'N{index + 1:03d}'


def gap_mark(gap):
    what = 'foreign script' if gap['reason'] == 'foreign' else f"{gap['extent']} illegible"
    return f"{{G{gap['index'] + 1:03d}: {what}}}"


def render(raw, decisions, gaps):
    """Markers made editorial marks; `decisions` is an iterator over this text's join rows."""
    def replace(match):
        if match.group(1):
            return gap_mark(gaps[int(match.group(1))])
        if match.group(2):
            return f'[{note_id(int(match.group(2)))}]'
        if match.group(3):
            return f'{{No. {match.group(3)}}}'
        return '-' if next(decisions)['decision'] == 'hyphen' else ''
    raw = LAYOUT_AT_BREAK.sub(r'\1', raw)  # a word broken at a line end has no space of its own
    return re.sub(r'\s+', ' ', MARKER.sub(replace, raw)).strip()


def note_kind(text):
    """'gap-only', 'reference' (citations only, by a rule of thumb) or 'prose'.

    A reference has a number or a citation word (lib., cap. …), and at most two of its words
    are neither abbreviations, numbers nor citation words.
    """
    rest = textnorm.GAP_MARK.sub(' ', text)
    if not textnorm.words(rest):
        return 'gap-only'
    tokens = rest.split()
    keys = [textnorm.key(t) for t in tokens]
    if not any(re.search(r'\d', t) for t in tokens) and not REFERENCE_SIGNS & set(keys):
        return 'prose'
    other = [t for t, k in zip(tokens, keys)
             if k and not t.endswith('.') and not k.isdigit() and k not in REFERENCE_WORDS
             and not re.fullmatch(r'[\d.,:;&]+', t)]
    return 'reference' if len(other) <= 2 else 'prose'


def italics(where, text, out):
    for match in ITALIC.finditer(text):
        span = re.sub(r'\s+', ' ', textnorm.NOTE_ANCHOR.sub('', match.group(1))).strip()
        if span:
            out.append({'in': where, 'text': span})
    return text.replace(tei.ITALIC_ON, '').replace(tei.ITALIC_OFF, '')


def build(source):
    preface = tei.parse(source)
    paragraphs = [(s.id, p) for s in preface.sections for p in s.paragraphs]
    notes_of = {}
    for note in preface.notes:
        notes_of.setdefault(note.paragraph, []).append(note)
    order = []  # every text in reading order: a paragraph, then its notes
    for _, p in paragraphs:
        order.append(('paragraph', p.id, p.raw))
        order += [('note', note_id(n.index), n.raw) for n in notes_of.get(p.id, [])]
    rows = joins.decide([raw for _, _, raw in order])
    for row in rows:
        row['in'], row['id'] = order[row.pop('text')][:2]
    pending = iter(rows)
    rendered, italic_spans = {}, []
    for _, where, raw in order:
        rendered[where] = italics(where, render(raw, pending, preface.gaps), italic_spans)

    verse = {p.id for _, p in paragraphs if p.kind == 'verse'}
    notes = [{'id': note_id(n.index), 'paragraph': n.paragraph, 'kind': note_kind(rendered[note_id(n.index)]),
              'in_verse': n.paragraph in verse, 'words': len(textnorm.words(rendered[note_id(n.index)])),
              'text': rendered[note_id(n.index)]} for n in preface.notes]
    paras = [{'id': p.id, 'section': sid, 'kind': p.kind, 'words': len(textnorm.words(rendered[p.id])),
              'note_words': sum(n['words'] for n in notes if n['paragraph'] == p.id), 'text': rendered[p.id]}
             for sid, p in paragraphs]
    gaps = [{'id': f"G{g['index'] + 1:03d}", 'paragraph': g['paragraph'],
             'note': None if g['note'] is None else note_id(g['note']), 'reason': g['reason'],
             'extent': g['extent']} for g in preface.gaps]
    sections = []
    for s in preface.sections:
        mine = [p for p in paras if p['section'] == s.id]
        ids = {p['id'] for p in mine}
        sections.append({'id': s.id, 'label': textnorm.printed(mine[0]['text']), 'first': mine[0]['id'],
                         'last': mine[-1]['id'], 'paragraphs': len(mine), 'words': sum(p['words'] for p in mine),
                         'note_words': sum(p['note_words'] for p in mine),
                         'notes': sum(n['paragraph'] in ids for n in notes),
                         'gaps': sum(g['paragraph'] in ids for g in gaps)})
    table = chunks.build([(p['section'], p['id'], p['words'] + p['note_words']) for p in paras])
    return {'sections': sections, 'chunks': table, 'paragraphs': paras, 'notes': notes, 'gaps': gaps,
            'italics': italic_spans, 'joins': rows}


def to_json(data):
    return json.dumps(data, ensure_ascii=False, indent=1) + '\n'


def main():
    out = build(paths.SOURCE)
    with open(paths.SOURCE, 'rb') as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    notes_of = {}
    for note in out['notes']:
        notes_of.setdefault(note['paragraph'], []).append(note)
    for section in out['sections']:
        lines = []
        for p in (p for p in out['paragraphs'] if p['section'] == section['id']):
            lines.append(f"{p['id']} {p['text']}\n")
            lines += [f"{n['id']} {n['text']}\n" for n in notes_of.get(p['id'], [])]
        paths.write(os.path.join(paths.TEXT, f"{section['id']}.txt"), ''.join(lines))
    doubtful = [r for r in out.pop('joins') if r['decision'] == 'hyphen' or r['basis'] == 'both-words']
    paths.write(os.path.join(paths.TEXT, 'joins.json'), to_json(doubtful))
    paths.write(os.path.join(paths.TEXT, 'preface.json'),
                to_json({'source': 'sources/A74670.xml', 'sha256': digest, **out}))
    for s in out['sections']:
        print(s['id'], s['paragraphs'], 'paragraphs', s['words'], 'words +', s['note_words'], 'in notes')
    print(len(out['chunks']), 'chunks:', ' '.join(f"{c['id']}={c['words']}" for c in out['chunks']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
