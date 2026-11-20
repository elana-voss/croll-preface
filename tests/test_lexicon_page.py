import unittest

import fixture  # noqa: F401 (puts scripts/ on the path)
import lexicon_page

ENTRY = {'headword': 'physic', 'spellings': ['Physick', 'Phisick'],
         'senses': [{'sense': 'The art of healing.', 'use': 'plain', 'reading': 'Stated', 'voice': 'CROLL',
                     'tags': ['note-only'], 'evidence': [{'ref': 'N001', 'quote': 'true Physick'}]}]}


class LexiconPageTest(unittest.TestCase):
    def test_an_entry_shows_spellings_each_sense_its_marks_and_quoted_evidence(self):
        page = lexicon_page.render([dict(ENTRY, headword='seed', spellings=['Seed']), ENTRY])
        self.assertLess(page.index('## Physic'), page.index('## Seed'))
        self.assertIn('The book spells it: Physick, Phisick', page)
        self.assertIn('1. The art of healing. *(plain · Stated · voice: CROLL · note-only)*', page)
        self.assertIn('   - “true Physick” [N001]', page)


if __name__ == '__main__':
    unittest.main()
