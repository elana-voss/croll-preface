"""Every quotation in an output must stand, word for word, where its reference says."""
import argparse
import re
import sys

import outputs
import preface
import textnorm

MAX_WORDS = 40
ELLIPSIS = re.compile(r'…|\.\s*\.\s*\.')


def _short(quote):
    return ' '.join(quote.split()[:8])


def _resolve(book, ref):
    """The ids of a reference that may list several places, split by ';', and its problems."""
    ids, problems = [], []
    for part in outputs.refs_in(ref):
        found = book.expand(part)
        if found is None:
            problems.append(f'unresolved reference {part}')
        else:
            ids += found
    return ids, problems


def check_quote(book, ref, quote):
    ids, problems = _resolve(book, ref)
    if not outputs.refs_in(ref):
        problems.append('no reference')
    if not quote.strip():
        problems.append('empty quote')
    elif not textnorm.words(textnorm.ANY_BRACES.sub(' ', quote)):
        problems.append('no words outside gaps')
    if ELLIPSIS.search(quote):
        problems.append('ellipsis in quote')
    if len(quote.split()) > MAX_WORDS:
        problems.append(f'over {MAX_WORDS} words')
    if ids and textnorm.words(textnorm.ANY_BRACES.sub(' ', quote)) and not book.find(ids, quote):
        elsewhere = book.locate(quote)
        problems.append(f"wrong reference, found at {', '.join(elsewhere[:3])}" if elsewhere else 'not found')
    return [f'{ref}: {problem}: "{_short(quote)}"' for problem in problems]


def _items(data):
    """Every dictionary in a JSON value."""
    if isinstance(data, dict):
        yield data
        data = list(data.values())
    if isinstance(data, list):
        for value in data:
            yield from _items(value)


def check_json(book, data):
    problems = []
    for item in _items(data):
        if 'quote' not in item:
            continue
        if not isinstance(item['quote'], str) or not isinstance(item.get('ref', ''), str):
            problems.append(f'quote or reference is not text: {item!r}'[:120])
        elif 'ref' not in item:
            problems.append(f"quote without reference: \"{_short(item['quote'])}\"")
        else:
            problems += check_quote(book, item['ref'], item['quote'])
    return problems


def _check_paragraph(book, paragraph):
    brackets = [(m.start(), m.group(1)) for m in outputs.REF_BRACKET.finditer(paragraph)]
    problems = [f'unresolved reference {ref}' for _, bracket in brackets for ref in outputs.refs_in(bracket)
                if book.expand(ref) is None]
    if paragraph.count('“') != paragraph.count('”'):
        problems.append(f'unbalanced curly quotation marks: "{_short(paragraph)}"')
    for quote in outputs.PAGE_QUOTE.finditer(paragraph):
        following = [bracket for at, bracket in brackets if at >= quote.end()]
        if not following or not outputs.refs_in(following[0]):
            problems.append(f'quote with no reference in its paragraph: "{_short(quote.group(1))}"')
            continue
        usable = [ref for ref in outputs.refs_in(following[0]) if book.expand(ref) is not None]
        if usable:
            problems += check_quote(book, '; '.join(usable), quote.group(1))
    return problems


def check_page(book, text):
    body = outputs.page_body(text)
    problems = [p for paragraph in re.split(r'\n\s*\n', body) for p in _check_paragraph(book, paragraph)]
    if '"' in body:
        problems.append('straight quotation mark in page')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    book = preface.load()
    problems = []
    for path in args.paths:
        try:
            found = check_json(book, outputs.load_json(path)) if outputs.is_json(path) else check_page(book, outputs.read(path))
        except (OSError, ValueError) as error:
            found = [f'unreadable: {error}']
        problems += [f'{path}: {problem}' for problem in found]
    return outputs.report(problems, 'all quotes pass')


if __name__ == '__main__':
    sys.exit(main())
