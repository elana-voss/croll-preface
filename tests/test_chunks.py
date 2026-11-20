import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import chunks  # noqa: E402


class ChunksTest(unittest.TestCase):
    def test_a_section_is_cut_at_paragraphs_into_near_equal_chunks_under_the_cap(self):
        paragraphs = [('A', 'A.1', 30), ('A', 'A.2', 30), ('A', 'A.3', 30), ('A', 'A.4', 30), ('A', 'A.5', 100),
                      ('B', 'B.1', 50), ('B', 'B.2', 60), ('B', 'B.3', 50)]
        table = chunks.build(paragraphs, max_words=100)
        self.assertEqual([(c['id'], c['first'], c['last'], c['words']) for c in table],
                         [('A-1', 'A.1', 'A.2', 60), ('A-2', 'A.3', 'A.4', 60), ('A-3', 'A.5', 'A.5', 100),
                          ('B-1', 'B.1', 'B.1', 50), ('B-2', 'B.2', 'B.2', 60), ('B-3', 'B.3', 'B.3', 50)])


if __name__ == '__main__':
    unittest.main()
