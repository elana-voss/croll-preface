import unittest

import fixture  # noqa: F401 (puts scripts/ on the path)
import unit_lines

UNIT = {'id': 'U1', 'marked_at': [{'ref': 'N001', 'quote': 'Damascen'}], 'parts': []}
OBSERVATIONS = [{'ref': 'OPEN.2', 'quote': 'Medicines'}, {'ref': 'OPEN.2', 'quote': 'few'},
                {'ref': 'OPEN.0', 'quote': 'Preface'}, {'ref': 'CH1.0', 'quote': 'CHAP'}]


class UnitLinesTest(unittest.TestCase):
    def test_the_cited_lines_always_then_observed_paragraphs_of_their_sections_while_they_fit(self):
        book = fixture.book()
        self.assertEqual(unit_lines.choose(book, UNIT, OBSERVATIONS, 0), {'OPEN.1'})
        self.assertEqual(unit_lines.choose(book, UNIT, OBSERVATIONS, 10_000), {'OPEN.0', 'OPEN.1', 'OPEN.2'})

    def test_a_long_quote_is_cut_to_a_locator(self):
        self.assertEqual(unit_lines.locator({'quote': 'a' * 60, 'ref': 'X'}), {'quote': 'a' * 50 + ' …', 'ref': 'X'})
        self.assertEqual(unit_lines.locator({'quote': 'short'}), {'quote': 'short'})


if __name__ == '__main__':
    unittest.main()
