import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import joins  # noqa: E402
from tei import EOL, EOL_PLAIN  # noqa: E402


class JoinsTest(unittest.TestCase):
    def setUp(self):
        texts = ['Some-thing, anywhere, in and deed.',
                 f'some{EOL}thing any{EOL}where Bom{EOL}baſt in{EOL}deed ever{EOL_PLAIN}more']
        self.rows = [(r['left'], r['right'], r['decision'], r['basis']) for r in joins.decide(texts)]

    def test_each_break_is_decided_from_the_preface_itself(self):
        self.assertEqual(self.rows, [
            ('some', 'thing', 'hyphen', 'hyphenated-elsewhere'),
            ('any', 'where', 'join', 'joined-elsewhere'),
            ('Bom', 'baſt', 'join', 'default'),
            ('in', 'deed', 'join', 'both-words'),
            ('ever', 'more', 'join', 'unhyphenated'),
        ])


if __name__ == '__main__':
    unittest.main()
