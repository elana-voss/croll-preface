import unittest

import fixture  # noqa: F401 (puts scripts/ on the path)
import candidates

R = {'observations': [
    {'ref': 'OPEN.2', 'type': 'marking', 'quote': 'Let thy Medicines be few', 'what': 'few Medicines', 'voice': 'CROLL',
     'tags': ['note-only'], 'from': ['A1', 'B1'], 'note': 'A long note ' * 20},
    {'ref': 'OPEN.1', 'type': 'voice', 'quote': 'Not he that knowes', 'voice': 'QUOTED: Damascen', 'from': ['A2'],
     'note': 'Another long note ' * 20}],
    'dropped': [{'from': 'B2', 'reason': 'a name only'}]}


class CandidatesTest(unittest.TestCase):
    def test_every_observation_stays_one_line_and_notes_shorten_to_fit_the_budget(self):
        full = candidates.compact(R, budget=10_000)
        self.assertEqual(full.count('\n'), 1)
        self.assertIn('OPEN.2 | marking | CROLL | note-only | “Let thy Medicines be few” | few Medicines | A long note', full)
        small = candidates.compact(R, budget=80)
        self.assertLessEqual(candidates.bundle.tokens(small), 80)
        self.assertEqual(small.count('\n'), 1)
        self.assertIn('“Not he that knowes”', small)


if __name__ == '__main__':
    unittest.main()
