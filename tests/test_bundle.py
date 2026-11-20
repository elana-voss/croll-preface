import os
import tempfile
import unittest

import fixture  # first: it puts scripts/ on the path
import bundle  # noqa: I100
import prompt_check


class BundleTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.prompt = os.path.join(self.folder, 'task.md')
        with open(self.prompt, 'w', encoding='utf-8') as f:
            f.write('# Task\nRead the text.\n')
        self.lists = prompt_check.Lists(plain={'task', 'read', 'the', 'text'}, reviewed={'the'}, book_words={'the'})

    def build(self, parts, max_tokens=1000, prompt=None):
        return bundle.build(fixture.book(), 'b', [prompt or self.prompt], parts, [('UNVERIFIED CANDIDATE', self.prompt)],
                            max_tokens, self.lists, folder=self.folder)

    def test_the_text_shows_each_paragraph_then_its_notes_with_long_s_typed_as_s(self):
        text = self.build(['OPEN-2', 'OPEN-1'])['text']
        self.assertIn('=== SECTION OPEN: THE Preface ===\nOPEN.0 THE Preface\n'
                      'OPEN.1 Not he that knowes many things[N001] is wise.\nN001 (margin note to OPEN.1) Damascen.\n'
                      'OPEN.2 Let thy Medicines be few, saith one.\n', text)
        self.assertIn('######## UNVERIFIED CANDIDATE: task.md ########', text)
        self.assertEqual(self.build(['OPEN-2'])['text'].count(bundle.LEFT_OUT), 1)

    def test_a_bundle_over_its_limit_or_with_an_unchecked_prompt_word_is_refused(self):
        with self.assertRaisesRegex(bundle.BundleError, 'over the limit'):
            self.build(['OPEN'], max_tokens=10)
        bad = os.path.join(self.folder, 'bad.md')
        with open(bad, 'w', encoding='utf-8') as f:
            f.write('Read the Medicines.\n')
        with self.assertRaisesRegex(bundle.BundleError, 'bad.md: medicines'):
            self.build(['OPEN'], prompt=bad)


class PromptCheckTest(unittest.TestCase):
    def test_a_prompt_word_is_flagged_if_the_book_has_it_or_it_is_not_plain_unless_reviewed(self):
        lists = prompt_check.Lists(plain={'read', 'the', 'book', 'and', 'wise', 'men'}, reviewed={'the', 'and', 'read'},
                                   book_words={'the', 'wise', 'men', 'and', 'read'})
        self.assertEqual(prompt_check.flagged("Read the book's text and wise men, end_marker", lists),
                         ['end', 'marker', 'men', 'text', 'wise'])


if __name__ == '__main__':
    unittest.main()
