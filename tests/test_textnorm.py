import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import textnorm  # noqa: E402

PARAGRAPH = '{No. I} The ſpirit of the {G007: 2 letters illegible}orld[N012] is one ſpirit.'


class TextnormTest(unittest.TestCase):
    def test_long_s_case_whitespace_and_line_end_hyphens_fold(self):
        self.assertEqual(textnorm.normalise('The  ſpi-\n  rit\nIS'), 'the spirit is')

    def test_a_quote_matches_with_the_gap_written_in_any_braces(self):
        self.assertTrue(textnorm.find_quote('spirit of the {gap}orld', PARAGRAPH))
        self.assertTrue(textnorm.find_quote('ſpirit of the {G007: 2 letters illegible}orld', PARAGRAPH))

    def test_a_guessed_gap_does_not_match(self):
        self.assertFalse(textnorm.find_quote('spirit of the world', PARAGRAPH))

    def test_a_quote_may_not_span_a_note_anchor(self):
        self.assertFalse(textnorm.find_quote('orld is one', PARAGRAPH))
        self.assertTrue(textnorm.find_quote('is one spirit', PARAGRAPH))

    def test_words_leave_out_markers(self):
        self.assertEqual(textnorm.words(PARAGRAPH),
                         ['the', 'spirit', 'of', 'the', 'orld', 'is', 'one', 'spirit'])

    def test_a_word_with_an_apostrophe_is_one_and_an_ampersand_is_one(self):
        self.assertEqual(textnorm.words("Aſtra's & Nature's"), ["astra's", '&', "nature's"])

    def test_a_gap_inside_a_word_does_not_split_it(self):
        self.assertEqual(textnorm.words('lea{G010: 2 letters illegible}ned well'), ['leaned', 'well'])

    def test_a_quote_must_start_and_end_on_whole_words(self):
        self.assertFalse(textnorm.find_quote('pirit of th', PARAGRAPH))


if __name__ == '__main__':
    unittest.main()
