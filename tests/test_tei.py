import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import tei  # noqa: E402


class TeiTest(unittest.TestCase):
    def test_an_expanded_abbreviation_joins_its_word_without_the_layout_spaces(self):
        el = ET.fromstring('<p>ſua per<expan>\n   <am><g ref="char:abque"/></am>\n   <ex>que</ex>\n  </expan>Ae</p>')
        self.assertEqual(tei._Reader().inline(el), 'ſua perqueAe')


if __name__ == '__main__':
    unittest.main()
