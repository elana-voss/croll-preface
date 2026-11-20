import unittest

import fixture  # noqa: F401 (puts scripts/ on the path)
import lexicon_lines

ROWS = [{'key': 'medicine', 'spellings': ['Medicine'], 'read_at': ['OPEN.2'], 'occurs_at': ['OPEN.2']},
        {'key': 'medicines', 'spellings': ['Medicines'], 'read_at': ['OPEN.2', 'N001'], 'occurs_at': ['OPEN.2']},
        {'key': 'few', 'spellings': ['few'], 'read_at': ['OPEN.2'], 'occurs_at': ['OPEN.2']}]


class LexiconLinesTest(unittest.TestCase):
    def test_a_spread_keeps_the_ends_and_the_order(self):
        self.assertEqual(lexicon_lines.spread(list('abcdefg'), 3), ['a', 'd', 'g'])
        self.assertEqual(lexicon_lines.spread(list('ab'), 5), ['a', 'b'])

    def test_variants_join_and_only_headwords_read_twice_stay(self):
        groups = lexicon_lines.groups(ROWS, [['medicine', 'medicines']], min_read=2)
        self.assertEqual(groups, [{'keys': ['medicine', 'medicines'], 'spellings': ['Medicine', 'Medicines'],
                                   'read_at': ['OPEN.2', 'N001'], 'occurs_at': ['OPEN.2']}])

    def test_a_batch_holds_headwords_while_their_lines_fit_and_one_alone_may_exceed(self):
        book = fixture.book()
        one = {'keys': ['a'], 'read_at': ['OPEN.1'], 'occurs_at': []}
        two = {'keys': ['b'], 'read_at': ['OPEN.2'], 'occurs_at': []}
        self.assertEqual(lexicon_lines.batches(book, [one, two], 10_000), [[one, two]])
        self.assertEqual(lexicon_lines.batches(book, [one, two], 1), [[one], [two]])


if __name__ == '__main__':
    unittest.main()
