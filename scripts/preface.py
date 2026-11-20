"""The extracted Preface as outputs cite it: ids, references, quotes, words."""
import json
import re

import paths
import textnorm

RUN = re.compile(r'([A-Z0-9]+)\.(\d+)\s*[–—-]\s*(?:\1\.)?(\d+)')  # OPEN.3–7 or OPEN.3–OPEN.7: paragraphs 3 to 7
NOTE_RUN = re.compile(r'N(\d+)\s*[–—-]\s*N?(\d+)')  # N012–N014


class Preface:
    def __init__(self, data):
        self.sections = {s['id']: s for s in data['sections']}
        self.chunks = {c['id']: c for c in data['chunks']}
        self.paragraphs = {p['id']: p for p in data['paragraphs']}
        self.notes = {n['id']: n for n in data['notes']}
        self.italics = data['italics']
        self.notes_of = {}
        for note in data['notes']:
            self.notes_of.setdefault(note['paragraph'], []).append(note['id'])
        self.order = [i for p in data['paragraphs'] for i in [p['id'], *self.notes_of.get(p['id'], [])]]
        self.texts = {i: (self.paragraphs.get(i) or self.notes[i])['text'] for i in self.order}
        self._words = None

    def expand(self, ref):
        """The ids a reference names, or None: `OPEN.3`, `N012`, a run `OPEN.3–7` (its paragraphs with their notes)
        or a run of notes `N012–N014`."""
        ref = ref.strip()
        if ref in self.texts:
            return [ref]
        run, note_run = RUN.fullmatch(ref), NOTE_RUN.fullmatch(ref)
        if run:
            first, last = int(run.group(2)), int(run.group(3))
            ids = [f'{run.group(1)}.{n}' for n in range(first, last + 1)]
            if first < last and all(i in self.paragraphs for i in ids):
                return [i for p in ids for i in [p, *self.notes_of.get(p, [])]]
        if note_run:
            first, last, width = int(note_run.group(1)), int(note_run.group(2)), len(note_run.group(1))
            ids = [f'N{n:0{width}d}' for n in range(first, last + 1)]
            if first < last and all(i in self.notes for i in ids):
                return ids
        return None

    def paragraph_ids(self, name):
        """The paragraphs of a chunk or a section, in order."""
        if name in self.chunks:
            chunk = self.chunks[name]
            ids = [p for p in self.paragraph_ids(chunk['section'])]
            return ids[ids.index(chunk['first']):ids.index(chunk['last']) + 1]
        if name in self.sections:
            return [p for p, row in self.paragraphs.items() if row['section'] == name]
        raise KeyError(f'unknown chunk or section {name}')

    def section_of(self, text_id):
        paragraph = self.notes[text_id]['paragraph'] if text_id in self.notes else text_id
        return self.paragraphs[paragraph]['section']

    def find(self, ids, quote):
        """The ids among `ids` whose text holds the quote."""
        return [i for i in ids if textnorm.find_quote(quote, self.texts[i])]

    def locate(self, quote):
        return self.find(self.order, quote)

    def words(self):
        """Every word of the Preface, normalised."""
        if self._words is None:
            self._words = {w for text in self.texts.values() for w in textnorm.words(text)}
        return self._words


def load(path=paths.PREFACE):
    with open(path, encoding='utf-8') as f:
        return Preface(json.load(f))
