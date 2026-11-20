import unittest

import fixture
import outside_check
import readings

A = {'items': [{'n': 1, 'ref': 'OPEN.2', 'type': 'marking', 'quote': 'Let thy Medicines be few'},
               {'n': 2, 'ref': 'OPEN.1', 'type': 'voice', 'quote': 'Not he that knowes', 'name': 'one'}]}
B = {'items': [{'n': 1, 'ref': 'OPEN.2', 'type': 'marking', 'quote': 'Medicines be few'},
               {'n': 2, 'ref': 'N001', 'type': 'voice', 'quote': 'Damascen'}]}
R = {'observations': [
    {'ref': 'OPEN.2', 'type': 'marking', 'quote': 'Let thy Medicines be few', 'what': 'few Medicines', 'term': 'Medicines',
     'voice': 'CROLL', 'from': ['A1', 'B1']},
    {'ref': 'OPEN.1', 'type': 'voice', 'quote': 'Not he that knowes', 'voice': 'QUOTED: Damascen', 'from': ['A2']}],
    'dropped': [{'from': 'B2', 'reason': 'a name only'}],
    'voices': [{'ref': 'OPEN.1', 'voice': 'QUOTED: Damascen', 'quote': 'Not he that knowes many things', 'basis': 'note'}]}


class ReadingsTest(unittest.TestCase):
    def test_the_trial_counts_reconciled_observations_found_by_one_reader_only(self):
        self.assertEqual(readings.trial([('OPEN-1', A, B, R)]),
                         ({'observations': 2, 'one_reader': 1, 'share': 0.5, 'only_A': 1, 'only_B': 0}, []))

    def test_every_reader_item_is_kept_or_dropped_and_every_source_exists(self):
        bad = {**R, 'dropped': [], 'observations': R['observations'] + [{'ref': 'OPEN.2', 'from': ['B9']}]}
        self.assertEqual(readings.trial([('OPEN-1', A, B, bad)])[1],
                         ['OPEN-1: B9 is no reader item', 'OPEN-1: observation 3 has no source',
                          'OPEN-1: B2 neither kept nor dropped'])

    def test_malformed_sources_are_reported_not_counted(self):
        bad = {'observations': R['observations'] + [{'ref': 'OPEN.2', 'from': ['a1', '', 3]}, {'ref': 'OPEN.2'}],
               'dropped': [{'from': 'B2'}, {'from': 'A1'}]}
        figure, problems = readings.trial([('OPEN-1', A, {'items': B['items'] + [{'ref': 'x'}]}, bad)])
        self.assertEqual(figure['observations'], 2)
        self.assertEqual(problems, ['OPEN-1: reader B item without a number',
                                    "OPEN-1: a1 is no reader item", "OPEN-1:  is no reader item", 'OPEN-1: 3 is no reader item',
                                    'OPEN-1: A1 both kept and dropped', 'OPEN-1: observation 3 has no source',
                                    'OPEN-1: observation 4 has no source'])

    def test_consumers_skip_malformed_entries(self):
        odd = {'observations': [{'type': 'marking', 'ref': ['OPEN.2'], 'term': ['x']}, {'type': 'marking'}],
               'voices': ['a name']}
        self.assertEqual(readings.markings(fixture.book(), [('OPEN-1', odd)]), [])
        self.assertEqual(readings.voices([('OPEN-1', odd)]), [])
        self.assertEqual([w['read_at'] for w in readings.headwords(fixture.book(), [('OPEN-1', odd)])], [[], []])

    def test_markings_voices_and_headwords_are_listed_from_the_reconciled_readings(self):
        book = fixture.book()
        self.assertEqual(readings.markings(book, [('OPEN-1', R)]),
                         [{'chunk': 'OPEN-1', 'ref': 'OPEN.2', 'quote': 'Let thy Medicines be few', 'what': 'few Medicines',
                           'voice': 'CROLL', 'tags': []}])
        self.assertEqual(readings.voices([('OPEN-1', R)]), [{'chunk': 'OPEN-1', **R['voices'][0]}])
        words = readings.headwords(book, [('OPEN-1', R)])
        self.assertEqual(words[0], {'key': 'medicines', 'spellings': ['Medicines'], 'read_at': ['OPEN.2'],
                                    'italic_at': ['OPEN.2'], 'occurs_at': ['OPEN.2']})
        self.assertEqual([w['key'] for w in words], ['medicines', 'damascen'])


class OutsideCheckTest(unittest.TestCase):
    def test_words_neither_in_the_book_nor_plain_are_listed(self):
        found = outside_check.outside(fixture.book(), {'type': 'zzz', 'detail': 'Medicines and qwerty, qwerty'}, {'and'})
        self.assertEqual(found, {'qwerty': 2})

    def test_a_possessive_outside_word_is_listed_by_its_stem(self):
        self.assertEqual(outside_check.outside(fixture.book(), "qwerty's", set()), {'qwerty': 1})

    def test_a_name_the_book_prints_only_as_a_possessive_is_the_books(self):
        class Book:
            def words(self):
                return {"noe's"}
        self.assertEqual(outside_check.outside(Book(), "Noe's time", {'time'}), {})

    def test_a_link_target_is_not_prose(self):
        self.assertEqual(outside_check.prose('[Medicines](units/qwerty.md)'), '[Medicines]')


if __name__ == '__main__':
    unittest.main()
