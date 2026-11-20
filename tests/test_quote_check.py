import unittest

import fixture
import quote_check


class QuoteCheckTest(unittest.TestCase):
    def setUp(self):
        self.book = fixture.book()

    def test_a_quote_must_stand_whole_where_its_reference_says(self):
        long = ' '.join(['few'] * 41)
        found = [quote_check.check_quote(self.book, ref, quote) for ref, quote in [
            ('OPEN.2', 'Let thy Medicines be few, saith'), ('OPEN.1', 'Let thy Medicines'), ('OPEN.2', 'Let thy Physick'),
            ('OPEN.2', 'Let thy … few'), ('OPEN.2', long), ('OPEN.7', 'Let thy'), ('OPEN.1', 'many things is wise')]]
        self.assertEqual(found[0], [])
        self.assertIn('found at OPEN.2', found[1][0])
        self.assertIn('not found', found[2][0])
        self.assertIn('ellipsis', found[3][0])
        self.assertIn('over 40 words', found[4][0])
        self.assertIn('unresolved reference OPEN.7', found[5][0])
        self.assertIn('not found', found[6][0])  # runs across a note anchor

    def test_every_quote_of_a_json_output_is_checked(self):
        data = {'items': [{'ref': 'N001', 'quote': 'Damascen'},
                          {'ref': 'OPEN.1', 'quote': 'knowes many', 'with': {'ref': 'OPEN.2', 'quote': 'be many'}},
                          {'quote': 'few'}]}
        problems = quote_check.check_json(self.book, data)
        self.assertEqual(len(problems), 2)
        self.assertIn('be many', problems[0])
        self.assertIn('quote without reference', problems[1])

    def test_a_blank_reference_or_a_quote_of_only_a_gap_fails(self):
        found = quote_check.check_json(self.book, {'items': [{'ref': ' ; ', 'quote': 'zzz'}, {'ref': 'N001', 'quote': '{gap}'}]})
        self.assertEqual(len(found), 2, found)
        self.assertIn('no reference', found[0])
        self.assertIn('no words', found[1])

    def test_a_page_quote_takes_the_next_reference_of_its_paragraph(self):
        page = ('# Title\n\nHe says “Let thy Medicines be few” [OPEN.2] and see [the other page](other.md).\n\n'
                'Unplaced “Not he that knowes”.\n\nA “wise” man [OPEN.9].\n\nIt says "few" [OPEN.2].\n')
        problems = quote_check.check_page(self.book, page)
        self.assertEqual(len(problems), 3, problems)
        self.assertIn('no reference', problems[0])
        self.assertIn('unresolved reference OPEN.9', problems[1])
        self.assertIn('straight quotation mark', problems[2])

    def test_a_page_quote_left_open_or_before_a_blank_bracket_fails(self):
        problems = quote_check.check_page(self.book, 'He says “zzz [OPEN.2].\n\nShe says “zzz” [ ].\n')
        self.assertEqual(len(problems), 2, problems)
        self.assertIn('unbalanced', problems[0])
        self.assertIn('no reference', problems[1])


if __name__ == '__main__':
    unittest.main()
