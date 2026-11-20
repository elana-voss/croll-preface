"""The extraction against the XML itself: every printed sign, word, note and gap of the Preface."""
import collections
import pathlib
import re
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import extract  # noqa: E402
import tei  # noqa: E402
import textnorm  # noqa: E402

NS = '{http://www.tei-c.org/ns/1.0}'
SOURCE = ROOT / 'sources' / 'A74670.xml'
BREAK, GAP = '\x02', '\x03'  # a gap between a space and a break keeps the space
BLOCKS = {'head', 'p', 'l', 'note', 'opener', 'salute', 'closer', 'q'}


def printed(text):
    """Printed signs only: no spaces, no hyphens (joins may add or drop them), no verse slashes."""
    return ''.join(c for c in text if not c.isspace() and c not in '-/')


def from_xml():
    """(main text, notes text) of the Preface, read from the XML without the extraction's code."""
    body = ET.parse(SOURCE).getroot().find(f'{NS}text/{NS}group/{NS}text/{NS}body')
    main, notes = [], []

    def visit(el, into):
        tag = el.tag.replace(NS, '')
        if tag == 'gap':
            into.append(GAP)
            return
        if tag == 'g' and el.get('ref', '').startswith('char:EOL'):
            into.append(BREAK)
            return
        if tag == 'expan':  # the abbreviation sign is replaced by its expansion
            into.append(''.join(ex.text or '' for ex in el.iter(f'{NS}ex')))
            return
        if tag == 'note':
            into = notes
            notes.append(' ')
        into.append(el.text or '')
        for child in el:
            visit(child, into)
            into.append(child.tail or '')
        if tag in BLOCKS:
            into.append(' ')

    visit(body, main)
    return tuple(re.sub(rf'\s*{BREAK}\s*', '', ''.join(part)).replace(GAP, '')  # a break is inside a word
                 for part in (main, notes))


class ExtractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = extract.build(SOURCE)
        cls.main = ' '.join(textnorm.printed(p['text']) for p in cls.out['paragraphs'])
        cls.notes = ' '.join(textnorm.printed(n['text']) for n in cls.out['notes'])

    def test_every_printed_sign_is_kept_in_order(self):
        xml_main, xml_notes = from_xml()
        self.assertEqual(printed(self.main), printed(xml_main))
        self.assertEqual(printed(self.notes), printed(xml_notes))

    def test_word_counts_match_the_xml_once_breaks_are_joined(self):
        xml_main, xml_notes = from_xml()
        hyphens = collections.Counter(j['in'] == 'note' for j in self.out['joins'] if j['decision'] == 'hyphen')
        self.assertEqual(len(textnorm.words(self.main)), len(textnorm.words(xml_main)) + hyphens[False])
        self.assertEqual(len(textnorm.words(self.notes)), len(textnorm.words(xml_notes)) + hyphens[True])
        self.assertEqual(sum(p['words'] for p in self.out['paragraphs']), len(textnorm.words(self.main)))
        self.assertEqual(sum(n['words'] for n in self.out['notes']), len(textnorm.words(self.notes)))

    def test_sections_notes_gaps_and_italics_are_all_there(self):
        out = self.out
        self.assertEqual([s['id'] for s in out['sections']],
                         ['OPEN', 'CH1', 'MICRO', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6'])
        self.assertTrue(out['sections'][1]['label'].startswith('CHAP. I. Of the True'))
        self.assertEqual(len(out['notes']), 319)
        self.assertEqual(sum(n['in_verse'] for n in out['notes']), 3)
        self.assertEqual(collections.Counter(g['note'] is None for g in out['gaps']), {True: 44, False: 196})
        self.assertEqual(sum(g['reason'] == 'foreign' for g in out['gaps']), 22)
        self.assertEqual(len(out['italics']), 785)
        self.assertEqual(sum(p['kind'] == 'verse' for p in out['paragraphs']), 3)

    def test_each_note_and_gap_is_marked_once_where_it_stands(self):
        anchors = {p['id']: re.findall(r'\[(N\d+)\]', p['text']) for p in self.out['paragraphs']}
        mine = {p['id']: [n['id'] for n in self.out['notes'] if n['paragraph'] == p['id']] for p in self.out['paragraphs']}
        self.assertEqual(anchors, mine)
        texts = {p['id']: p['text'] for p in self.out['paragraphs']} | {n['id']: n['text'] for n in self.out['notes']}
        for gap in self.out['gaps']:
            self.assertEqual(texts[gap['note'] or gap['paragraph']].count('{' + gap['id'] + ':'), 1, gap['id'])

    def test_bare_references_are_told_from_prose(self):
        kinds = {text: extract.note_kind(text) for text in [
            'Mat. 9.1, 2.', 'Col. 3.17. & 1 Cor. 10.31.', 'Paracelſ. lib. de reſuſcitatione naturalium, ſol. 295.',
            'Hippocr. in lib. de Antiqua medic.', '{G001: foreign script} .', 'So is Man.',
            'The vitall ſpirit in Man & the Elemental is one ſpirit.',
            'John 1.3. Not by bread alone, Mat. 4.4. Grace exceedeth Nature.']}
        self.assertEqual(list(kinds.values()), ['reference'] * 4 + ['gap-only'] + ['prose'] * 3)


class RenderTest(unittest.TestCase):
    def test_no_layout_space_is_kept_beside_a_line_end_break(self):
        raw = f'lea{tei.GAP}0{tei.GAP}\n      {tei.EOL}ned'
        gaps = [{'index': 0, 'reason': 'illegible', 'extent': '2 letters'}]
        self.assertEqual(extract.render(raw, iter([{'decision': 'join'}]), gaps), 'lea{G001: 2 letters illegible}ned')


if __name__ == '__main__':
    unittest.main()
