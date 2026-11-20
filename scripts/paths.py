"""Where the source and the extracted text are, and how files are written."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'sources', 'A74670.xml')
TEXT = os.path.join(ROOT, 'text')
PREFACE = os.path.join(TEXT, 'preface.json')
WORK = os.path.join(ROOT, 'work')
BUNDLES = os.path.join(WORK, 'bundles')
READINGS = os.path.join(WORK, 'readings')
PROMPTS = os.path.join(ROOT, 'prompts')
PLAIN_ENGLISH = os.path.join(WORK, 'plain_english.txt')  # from Vim's spell file, not published


def write(path, text):
    """Write UTF-8 with LF line ends, creating the folder."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
