import unittest

import fixture  # noqa: F401 (puts scripts/ on the path)
import st_world


def entry(name, keys, content='x', order=100, gated=False, secondary=(), exclude=False, prevent=False):
    return {'name': name, 'key': keys, 'keysecondary': list(secondary), 'selective': gated, 'content': content,
            'order': order, 'excludeRecursion': exclude, 'preventRecursion': prevent}


class MatchTest(unittest.TestCase):
    def test_keys_match_whole_words_without_case_and_regex_keys_as_written(self):
        self.assertTrue(st_world.st_match('Seed', 'a seed.'))
        self.assertFalse(st_world.st_match('seed', 'the seeds'))
        self.assertTrue(st_world.st_match('/seeds?/i', 'the Seeds'))


class FireTest(unittest.TestCase):
    def test_gating_recursion_and_budget(self):
        entries = [entry('gated', ['art'], gated=True, secondary=['fire']),
                   entry('core', ['seed'], content='seed holds the stone'),
                   entry('reached', ['stone'], content='y' * 400, order=50),
                   entry('closed', ['holds'], exclude=True)]
        self.assertEqual(st_world.fire(entries, 'the art of painting'), ([], []))
        self.assertEqual(st_world.fire(entries, 'the art of fire and seed'), (['gated', 'core', 'reached'], []))
        self.assertEqual(st_world.fire(entries, 'a seed', budget=50), (['core'], ['reached']))


class ProblemsTest(unittest.TestCase):
    def test_bad_keys_are_named(self):
        found = st_world.key_problems('S', ['the stone', 'salt, sulphur', 'seed'])
        self.assertEqual(found, ['S: key starts with an article: the stone', 'S: comma in key: salt, sulphur',
                                 'S: no plural for: seed'])
        self.assertEqual(st_world.key_problems('S', ['seed', 'seeds', 'physic'], no_plural=['physic']), [])

    def test_content_with_references_labels_or_wrong_length_is_named(self):
        good = ' '.join(['word'] * 50)
        self.assertEqual(st_world.content_problems('S', good), [])
        self.assertEqual(st_world.content_problems('S', good + ' as in CH3.5'), ['S: reference'])
        self.assertEqual(st_world.content_problems('S', good + ' [N012]'), ['S: reference'])
        self.assertEqual(st_world.content_problems('S', 'Stated: ' + good), ['S: label'])
        self.assertEqual(st_world.content_problems('S', good + ' says the author'), ['S: label'])
        self.assertEqual(st_world.content_problems('S', 'too short'), ['S: 2 words'])


if __name__ == '__main__':
    unittest.main()
