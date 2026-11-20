import unittest

import fixture


class PrefaceTest(unittest.TestCase):
    def test_a_reference_names_a_paragraph_a_note_or_a_run_of_paragraphs(self):
        book = fixture.book()
        self.assertEqual([book.expand(ref) for ref in ['OPEN.1', ' N001 ', 'OPEN.0–2', 'OPEN.1-2', 'OPEN.1–9', 'OPEN']],
                         [['OPEN.1'], ['N001'], ['OPEN.0', 'OPEN.1', 'N001', 'OPEN.2'], ['OPEN.1', 'N001', 'OPEN.2'], None, None])

    def test_a_run_may_use_an_em_dash_repeat_its_section_or_list_notes(self):
        book = fixture.book()
        self.assertEqual([book.expand(ref) for ref in ['OPEN.1—2', 'OPEN.1–OPEN.2', 'N001–N001']],
                         [['OPEN.1', 'N001', 'OPEN.2'], ['OPEN.1', 'N001', 'OPEN.2'], None])

    def test_a_chunk_or_section_gives_its_paragraphs(self):
        book = fixture.book()
        self.assertEqual(book.paragraph_ids('OPEN-1'), ['OPEN.0', 'OPEN.1'])
        self.assertEqual(book.paragraph_ids('OPEN'), ['OPEN.0', 'OPEN.1', 'OPEN.2'])


if __name__ == '__main__':
    unittest.main()
