"""A three-paragraph Preface for the tests of what rests on the extraction."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import preface  # noqa: E402

DATA = {
    'sections': [{'id': 'OPEN', 'label': 'THE Preface'}, {'id': 'CH1', 'label': 'CHAP. I.'}],
    'chunks': [{'id': 'OPEN-1', 'section': 'OPEN', 'first': 'OPEN.0', 'last': 'OPEN.1'},
               {'id': 'OPEN-2', 'section': 'OPEN', 'first': 'OPEN.2', 'last': 'OPEN.2'},
               {'id': 'CH1-1', 'section': 'CH1', 'first': 'CH1.0', 'last': 'CH1.0'}],
    'paragraphs': [{'id': 'OPEN.0', 'section': 'OPEN', 'text': 'THE Preface'},
                   {'id': 'OPEN.1', 'section': 'OPEN', 'text': 'Not he that knowes many things[N001] is wiſe.'},
                   {'id': 'OPEN.2', 'section': 'OPEN', 'text': 'Let thy Medicines be few, ſaith one.'},
                   {'id': 'CH1.0', 'section': 'CH1', 'text': 'CHAP. I.'}],
    'notes': [{'id': 'N001', 'paragraph': 'OPEN.1', 'text': 'Damaſcen.'}],
    'italics': [{'in': 'OPEN.2', 'text': 'Medicines'}, {'in': 'N001', 'text': 'Damaſcen.'}],
}


def book():
    return preface.Preface(DATA)
