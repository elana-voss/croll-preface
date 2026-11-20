"""Read the Preface from the TEI source into sections of paragraphs, notes and gaps.

Line breaks inside words, gaps, notes, italics and printed numerals stay in the text as
private-use markers, so that later steps decide on them without parsing the XML again.
Any element or division not foreseen here stops the reading rather than being dropped.
"""
import dataclasses
import re
import xml.etree.ElementTree as ET

NS = '{http://www.tei-c.org/ns/1.0}'
EOL, EOL_PLAIN = '', ''          # word broken at a line end, with and without a hyphen
GAP, NOTE, NUMERAL = '', '', ''  # each wraps an index or a numeral
ITALIC_ON, ITALIC_OFF = '', ''
BREAKS = {'char:EOLhyphen': EOL, 'char:EOLunhyphen': EOL_PLAIN}
GAP_EXTENT = re.compile(r'\d+ (letters?|word|span)')


def local(el):
    return el.tag.replace(NS, '')


@dataclasses.dataclass
class Paragraph:
    id: str
    kind: str   # head, opener, p, verse, closer
    raw: str


@dataclasses.dataclass
class Section:
    id: str
    paragraphs: list


@dataclasses.dataclass
class Note:
    index: int
    paragraph: str
    raw: str


@dataclasses.dataclass
class Preface:
    sections: list
    notes: list
    gaps: list   # {'index', 'paragraph', 'note' (index or None), 'reason', 'extent'}


class _Reader:
    def __init__(self):
        self.out = Preface([], [], [])
        self.paragraph = None
        self.note = None

    def open(self, section_id):
        self.out.sections.append(Section(section_id, []))

    def add(self, kind, el):
        section = self.out.sections[-1]
        self.paragraph = f'{section.id}.{len(section.paragraphs)}'
        if (kind == 'head') != (not section.paragraphs):
            raise ValueError(f'{section.id} must open with its one head')
        raw = self.verse(el) if kind == 'verse' else self.inline(el)
        section.paragraphs.append(Paragraph(self.paragraph, kind, raw))

    def inline(self, el):
        parts = [el.text or '']
        for child in el:
            parts += [self.child(child), child.tail or '']
        return ''.join(parts)

    def verse(self, el):
        """A quoted verse: its lines joined by a slash."""
        lines = []
        for sub in el:
            if local(sub) != 'l' or (sub.tail or '').strip():
                raise ValueError(f'unexpected content in a verse: {local(sub)}')
            lines.append(self.inline(sub).strip())
        return ' / '.join(lines)

    def child(self, el):
        tag = local(el)
        if tag == 'g':
            if el.get('ref') in BREAKS:
                return BREAKS[el.get('ref')]
            if not el.text:
                raise ValueError(f"sign without text: {el.get('ref')}")
            return el.text
        if tag == 'gap':
            return self.gap(el)
        if tag == 'note':
            if self.note is not None:
                raise ValueError('note inside a note')
            self.note = len(self.out.notes)
            note = Note(self.note, self.paragraph, None)
            self.out.notes.append(note)
            note.raw = self.inline(el)
            self.note = None
            return f'{NOTE}{note.index}{NOTE}'
        if tag == 'hi':
            if el.get('rend') == 'sup':
                return self.inline(el)
            if el.get('rend'):
                raise ValueError(f"unexpected rendering {el.get('rend')}")
            return f'{ITALIC_ON}{self.inline(el)}{ITALIC_OFF}'
        if tag == 'milestone':
            return f'{NUMERAL}{el.get("n")}{NUMERAL}'
        if tag == 'pb' or tag == 'am':  # a page break; an abbreviation sign whose expansion follows
            return ''
        if tag == 'expan':  # an abbreviation sign and its expansion: the spaces between them are layout
            if (el.text or '').strip() or any((c.tail or '').strip() for c in el):
                raise ValueError('text loose inside an expansion')
            return ''.join(self.child(c) for c in el)
        if tag in ('seg', 'salute', 'ex'):
            return self.inline(el)
        raise ValueError(f'unexpected inline element {tag}')

    def gap(self, el):
        reason, extent = el.get('reason'), el.get('extent')
        if reason == 'foreign' and extent is None:
            pass
        elif reason != 'illegible' or not GAP_EXTENT.fullmatch(extent or ''):
            raise ValueError(f'unexpected gap {reason} {extent}')
        index = len(self.out.gaps)
        self.out.gaps.append({'index': index, 'paragraph': self.paragraph, 'note': self.note,
                              'reason': reason, 'extent': extent})
        return f'{GAP}{index}{GAP}'

    def walk(self, div):
        if (div.text or '').strip():
            raise ValueError('text outside any paragraph')
        for child in div:
            tag = local(child)
            if (child.tail or '').strip():
                raise ValueError(f'text outside any paragraph after {tag}')
            if tag == 'div':
                if child.get('type') != 'chapter':
                    raise ValueError(f"unexpected division {child.get('type')}")
                self.open(f"CH{child.get('n')}")
                self.walk(child)
            elif tag == 'q':
                self.add('verse', child)
            elif tag in ('head', 'opener', 'p', 'closer'):
                self.add(tag, child)
            elif tag != 'pb':
                raise ValueError(f'unexpected block element {tag}')

    def run(self, root):
        body = root.find(f'{NS}text/{NS}group/{NS}text/{NS}body')
        kinds = [div.get('type') for div in body]
        if kinds != ['preface', 'treatise']:
            raise ValueError(f'unexpected divisions of the Preface: {kinds}')
        for section_id, div in zip(('OPEN', 'MICRO'), body):
            self.open(section_id)
            self.walk(div)
        return self.out


def parse(path):
    return _Reader().run(ET.parse(path).getroot())
