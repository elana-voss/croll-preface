import unittest

import fixture  # noqa: F401 (puts scripts/ on the path)
import publish


class PageTest(unittest.TestCase):
    def test_trailer_is_cut_and_the_head_is_the_books(self):
        text = '# Chap. II. Where That\n\nBody [CH2.1].\n\nSECTIONS READ: CH2\nEND OF OUTPUT\n'
        self.assertEqual(publish.page(text, head='CHAP. II. Where that True Phyſick is to be Found.'),
                         '# Chapter II. Where that True Physick is to be Found\n\nBody [CH2.1].\n')

    def test_plain_page_loses_its_references_and_links_its_pointer(self):
        text = ('# U1 in Plain Language\n\nSays so [OPEN.2; N003]. See the page titled U1 in Plain Terms. [CH1.4–10]'
                '\n\nEND OF OUTPUT\n')
        self.assertEqual(publish.page(text, plain=('U1 in Plain Terms', 'U1.md')),
                         '# U1 in Plain Language\n\nSays so. See the page titled [U1 in Plain Terms](U1.md).\n')


class GateTest(unittest.TestCase):
    def test_images_broken_links_and_references_on_plain_pages_are_named(self):
        pages = {'a.md': 'x ![p](p.png) [b](sub/b.md) [c](c.md)', 'sub/b.md': 'y [a](../a.md) “quoted” [CH1.2]'}
        self.assertEqual(publish.gate(pages, plain=['sub/b.md']),
                         ['a.md: embedded image', 'a.md: broken link c.md', 'sub/b.md: reference', 'sub/b.md: quote'])

    def test_the_introduction_must_credit_the_transcription(self):
        self.assertEqual(publish.gate({'introduction.md': 'Our reading.'}), ['introduction.md: no TCP credit'])
        credit = 'Text Creation Partnership (TCP), CC0'
        self.assertEqual(publish.gate({'introduction.md': credit}), [])


if __name__ == '__main__':
    unittest.main()
