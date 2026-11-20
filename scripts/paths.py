"""Where the source and the extracted text are, and how files are written."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'sources', 'A74670.xml')
TEXT = os.path.join(ROOT, 'text')


def write(path, text):
    """Write UTF-8 with LF line ends, creating the folder."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
