"""One agent's whole reading: its prompts, its Preface text, labelled earlier outputs; refused over its limit."""
import argparse
import hashlib
import json
import os
import sys

import outputs
import paths
import preface
import prompt_check

LEFT_OUT = '[paragraphs not given here]'
# Geber measured 2.37 characters per token on a bundle with long s typed as s; 2.3 errs towards more tokens.
CHARS_PER_TOKEN = 2.3


class BundleError(Exception):
    pass


def tokens(text):
    return round(len(text) / CHARS_PER_TOKEN)


def _label(text):
    return f'######## {text} ########'


def _wanted(book, parts, paragraphs):
    wanted = set(paragraphs or ())
    for name in parts:
        try:
            wanted.update(book.paragraph_ids(name))
        except KeyError as error:
            raise BundleError(error.args[0]) from None
    unknown = wanted - set(book.paragraphs)
    if unknown:
        raise BundleError(f'unknown paragraph {sorted(unknown)[0]}')
    return wanted


def render(book, wanted):
    """The sections holding the wanted paragraphs, each paragraph followed by its notes."""
    out = []
    for sid, section in book.sections.items():
        ids = book.paragraph_ids(sid)
        if not wanted & set(ids):
            continue
        out.append(f"=== SECTION {sid}: {section['label']} ===")
        for pid in ids:
            if pid in wanted:
                out.append(f'{pid} {book.texts[pid]}')
                out += [f'{nid} (margin note to {pid}) {book.texts[nid]}' for nid in book.notes_of.get(pid, [])]
            elif out[-1] != LEFT_OUT:
                out.append(LEFT_OUT)
    return '\n'.join(out).replace('ſ', 's')


def build(book, name, prompts, parts, inputs, max_tokens, lists, folder=paths.BUNDLES, paragraphs=None):
    """Write the bundle and record it; `inputs` are (label, path) pairs, `paragraphs` extra paragraph ids."""
    flagged = prompt_check.problems(prompts, lists)
    if flagged:
        raise BundleError(f'prompt words not reviewed: {", ".join(flagged)}')
    wanted = _wanted(book, parts, paragraphs)
    blocks = [f'{_label("PROMPT: " + os.path.basename(p))}\n{outputs.read(p).rstrip()}' for p in prompts]
    blocks.append(f'{_label("PREFACE TEXT")}\n{render(book, wanted)}')
    blocks += [f'{_label(label + ": " + os.path.basename(p))}\n{outputs.read(p).rstrip()}' for label, p in inputs]
    text = '\n\n'.join(blocks) + '\n'
    if tokens(text) > max_tokens:
        raise BundleError(f'{name}: about {tokens(text):,} tokens, over the limit of {max_tokens:,}')
    entry = {'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(), 'tokens': tokens(text), 'parts': list(parts),
             'paragraphs': len(wanted), 'prompts': [os.path.basename(p) for p in prompts],
             'inputs': [[label, os.path.basename(p)] for label, p in inputs]}
    paths.write(os.path.join(folder, name + '.txt'), text)
    index = os.path.join(folder, 'index.json')
    stored = outputs.load_json(index) if os.path.exists(index) else {}
    stored[name] = entry
    paths.write(index, json.dumps(stored, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    return {**entry, 'text': text}


def _inputs(specs):
    pairs = []
    for spec in specs:
        label, _, path = spec.partition('=')
        if not label or not os.path.isfile(path):
            raise BundleError(f'bad --input {spec}: expected LABEL=path of an existing file')
        pairs.append((label, path))
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    parser.add_argument('--prompt', action='append', default=[])
    parser.add_argument('--part', action='append', default=[], help='chunk or section')
    parser.add_argument('--paragraph', action='append', default=[], help='one paragraph id')
    parser.add_argument('--input', action='append', default=[], help='LABEL=path of an earlier output')
    parser.add_argument('--max-tokens', type=int, required=True, help="the reader's limit: Fable 100000, Opus 70000")
    args = parser.parse_args()
    book = preface.load()
    try:
        entry = build(book, args.name, args.prompt, args.part, _inputs(args.input), args.max_tokens,
                      prompt_check.load(book), paragraphs=args.paragraph)
    except BundleError as error:
        return outputs.report([str(error)], '')
    return outputs.report([], f"{args.name}: {entry['paragraphs']} paragraphs, about {entry['tokens']:,} tokens")


if __name__ == '__main__':
    sys.exit(main())
