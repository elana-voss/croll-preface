import unittest

import fixture
import lorebook

ENTRIES = [{'headword': 'medicine', 'spellings': ['Medicines']}, {'headword': 'wise', 'spellings': ['wise']},
           {'headword': 'counsel', 'spellings': ['wise', 'few']}]
RULES = {'context': ['physic', 'healing'], 'open_keys': ['medicines'], 'no_plural': ['wisdom', 'wise'],
         'entries': [{'name': 'Medicine', 'headwords': ['medicine', 'Damascen'], 'keys': ['medicine', 'medicines'],
                      'tier': 1, 'gated': True},
                     {'name': 'Wisdom', 'headwords': ['wise'], 'keys': ['wisdom', 'wise'], 'tier': 2}]}


class IndexTest(unittest.TestCase):
    def test_places_sections_and_paired_page_make_a_subject_central(self):
        rows = lorebook.index_rows(fixture.book(), ENTRIES, 'Those medicines heal.', threshold=2)
        self.assertEqual(rows, [
            {'headword': 'medicine', 'places': 1, 'sections': 1, 'paired_page': True, 'central': True},
            {'headword': 'wise', 'places': 1, 'sections': 1, 'paired_page': False, 'central': False},
            {'headword': 'counsel', 'places': 2, 'sections': 1, 'paired_page': False, 'central': True}])


class RulesTest(unittest.TestCase):
    def test_unknown_headwords_headwords_twice_and_shared_keys_are_named(self):
        self.assertEqual(lorebook.check_rules(RULES, ['medicine', 'wise', 'Damascen']), [])
        bad = {**RULES, 'entries': RULES['entries'] + [
            {'name': 'Seed', 'headwords': ['seed', 'wise'], 'keys': ['wise', 'wisdom'], 'tier': 3}]}
        self.assertEqual(lorebook.check_rules(bad, ['medicine', 'wise', 'Damascen']), [
            'Seed: unknown headword seed', 'wise: in Wisdom and Seed', 'key on 2 subjects: wisdom (Wisdom, Seed)',
            'key on 2 subjects: wise (Wisdom, Seed)'])

    def test_a_gated_subject_with_nothing_to_gate_it_is_named(self):
        bare = {'context': ['medicine'], 'entries': [RULES['entries'][0]]}
        self.assertEqual(lorebook.check_rules(bare, ['medicine', 'Damascen']), ['Medicine: gated, but nothing gates it'])
        self.assertEqual(lorebook.st_entries(bare, {'Medicine': 'm'})[0]['keysecondary'], [])


class TriggerTest(unittest.TestCase):
    def test_a_wanted_subject_that_is_not_in_the_rules_is_named(self):
        self.assertEqual(lorebook.line_problems('Seeds; Medicine', 'a line', ['Medicine'], [], {'Medicine': 1}),
                         ['not a subject: Seeds: a line'])


class BuildTest(unittest.TestCase):
    def test_gated_entries_need_context_or_an_open_key_and_only_core_is_recursive(self):
        content = {'Medicine': 'm', 'Wisdom': 'w'}
        core, other = lorebook.st_entries(RULES, content)
        self.assertEqual((core['order'], core['selective'], core['excludeRecursion'], core['preventRecursion']),
                         (100, True, True, False))
        self.assertEqual(core['keysecondary'], ['physic', 'healing', 'medicines'])
        self.assertEqual(core['comment'], 'Medicine (word list: medicine, Damascen)')
        self.assertEqual((other['order'], other['selective'], other['excludeRecursion'], other['preventRecursion']),
                         (50, False, True, True))


if __name__ == '__main__':
    unittest.main()
