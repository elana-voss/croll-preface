"""Rights gate, then the finished pages into src/ and the mdBook build.
  python scripts/publish.py    write the pages into src/, gate every page and SUMMARY.md, run mdbook build
Each page loses the agent's trailer; a section page takes the book's own head; a Plain Language page loses its
references and links its pointer to the Plain Terms page. Gate (RIGHTS.md): the introduction credits the TCP
transcription, no page embeds an image, every link inside the book resolves, a Plain Language page holds no
reference or quote. Any problem fails the run before anything is written."""
import json, os, posixpath, re, subprocess, sys
from paths import PREFACE, ROOT, WORK, write

SRC = os.path.join(ROOT, 'src')
ONE = r'(?:(?:OPEN|MICRO|CH\d)\.\d+(?:–\d+)?|N\d{3})'
REFS = re.compile(rf'\s*\[{ONE}(?:; *{ONE})*\]')
LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)#\s]+)')
SECTIONS = ['OPEN', 'CH1', 'MICRO', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6']
UNITS = {'U1': 'The True Physic', 'U2': 'That One Only Chief Medicine of the Most Ancient Philosophers'}


def page(text, head=None, plain=None):
    """A finished page from an agent's output; `head` the book's head for its H1, `plain` (title, target) of the
    Plain Terms page a Plain Language page points to."""
    text = re.split(r'^(?:SECTIONS READ:|END OF OUTPUT)', text, maxsplit=1, flags=re.M)[0].rstrip() + '\n'
    if head:
        head = re.sub(r'^CHAP\. ', 'Chapter ', head.replace('ſ', 's')).rstrip('.')
        text = re.sub(r'\A# .*', lambda _: '# ' + head, text)
    if plain:
        title, target = plain
        text, n = re.subn(rf'([Tt]he page titled) {re.escape(title)}', rf'\1 [{title}]({target})', REFS.sub('', text))
        if n != 1:
            raise ValueError(f'pointer not found once: the page titled {title}')
    return text


def gate(pages, plain=()):
    """Problems in {published path: text}, by page."""
    problems = []
    for name, text in pages.items():
        found = ['embedded image'] * bool(re.search(r'!\[|<img', text, re.I))
        found += [f'broken link {t}' for t in LINK.findall(text) if not re.match(r'[a-z]+:', t)
                  and posixpath.normpath(posixpath.join(posixpath.dirname(name), t)) not in pages]
        if name in plain:
            found += [label for label, bad in (('reference', REFS.search(text)), ('quote', '“' in text)) if bad]
        if name == 'introduction.md' and not ('Text Creation Partnership' in text and 'CC0' in text):
            found.append('no TCP credit')
        problems += [f'{name}: {f}' for f in found]
    return problems


def _read(*parts):
    with open(os.path.join(WORK, *parts), encoding='utf-8') as f:
        return f.read()


def build():
    """{published path: text} for every page, and the Plain Language paths."""
    with open(PREFACE, encoding='utf-8') as f:
        heads = {s['id']: s['label'] for s in json.load(f)['sections']}
    pages = {'introduction.md': open(os.path.join(SRC, 'introduction.md'), encoding='utf-8').read()}
    for s in SECTIONS:
        pages[f'sections/{s}.md'] = page(_read('pages', f'{s}.corrected.md'),
                                         head=heads[s] if s.startswith('CH') else None)
    pages['synthesis.md'] = page(_read('synthesis', 'synthesis.corrected.md'))
    for u, title in UNITS.items():
        pages[f'units/{u}.md'] = page(_read('pairs', f'{u}.terms.corrected.md'))
        pages[f'units/{u}_plain.md'] = page(_read('pairs', f'{u}.plain.corrected.md'),
                                            plain=(f'{title} in Plain Terms', f'{u}.md'))
    pages['word_list.md'] = page(_read('lexicon', 'lexicon.md'))
    return pages, [f'units/{u}_plain.md' for u in UNITS]


def summary(pages):
    def item(p):
        return f'- [{pages[p].splitlines()[0][2:]}]({p})'
    lines = ['# Summary', '', '[Introduction](introduction.md)', '', '# The Preface, Section by Section', '']
    lines += [item(f'sections/{s}.md') for s in SECTIONS]
    lines += ['', '# The Whole and Its Two Subjects', '', item('synthesis.md')]
    lines += [item(f'units/{u}{x}.md') for u in UNITS for x in ('', '_plain')]
    lines += ['', '# Words', '', item('word_list.md')]
    return '\n'.join(lines) + '\n'


def main():
    pages, plain = build()
    pages['SUMMARY.md'] = summary(pages)
    problems = gate(pages, plain)
    if problems:
        print('GATE FAILED', *problems, sep='\n  ')
        sys.exit(1)
    for name, text in pages.items():
        write(os.path.join(SRC, *name.split('/')), text)
    print('gate passed;', len(pages), 'pages written')
    subprocess.run(['mdbook', 'build', ROOT], check=True)


if __name__ == '__main__':
    main()
