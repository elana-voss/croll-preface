"""Reading agents' outputs, and how a check reports."""
import json
import re
import sys

PAGE_QUOTE = re.compile(r'“([^“”]*)”')
REF_BRACKET = re.compile(r'\[([^\[\]]+)\](?!\()')  # a Markdown link `[text](target)` is not a reference
CLOSING = re.compile(r'\n(?:SECTIONS READ:|END OF OUTPUT).*', re.S)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def load_json(path):
    return json.loads(read(path))


def is_json(path):
    return path.lower().endswith('.json')


def page_body(text):
    """A page without its closing lines."""
    return CLOSING.sub('\n', text)


def refs_in(bracket):
    return [part.strip() for part in bracket.split(';') if part.strip()]


def report(problems, ok):
    """Print the problems, or `ok` if there are none; the exit code says which."""
    sys.stdout.reconfigure(encoding='utf-8')
    for problem in problems:
        print(problem)
    if not problems:
        print(ok)
    return 1 if problems else 0
