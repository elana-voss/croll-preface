"""The SillyTavern lorebook (LOREBOOK.md): an index of the word list, subjects, keys and merges from the rules file,
clean content written per batch from the checked word list, the JSON with its failure checks, and the trigger test.

  python lorebook.py index | rules | review | check_rules | batches | writer N | checker N | check FILE
                     | build [--placeholder] | lines | fire
"""
import argparse
import glob
import json
import os
import re
import sys

import bundle
import lexicon_lines
import lexicon_page
import outputs
import paths
import preface
import prompt_check
import readings
import st_world

FOLDER = os.path.join(paths.WORK, 'lorebook')
RULES = os.path.join(paths.ROOT, 'scripts', 'lorebook_rules.json')
OUT = os.path.join(paths.ROOT, 'lorebook', 'Croll_Admonitory_Preface.json')
OPUS, FABLE = 70_000, 100_000
BATCH = 25_000  # word-list text per content batch, leaving room for the candidate in the checker's bundle
ORDER = {1: 100, 2: 50, 3: 10}
END = 'END OF OUTPUT'
README = ("This lorebook holds the subjects of Croll's Admonitory Preface (Philosophy Reformed & Improved, London "
          '1657, Englished by H. Pinnell) as the Preface itself explains them. Recommended SillyTavern World Info settings: Recursive Scan on, Max '
          'Recursion Steps 2, Match Whole Words on, Case-sensitive off. This entry is disabled and never sent to the '
          'model.')


def path(name):
    return os.path.join(FOLDER, name)


def prompt(name):
    return os.path.join(paths.PROMPTS, name)


def lexicon():
    """{headword: entry} of every corrected word-list batch."""
    entries = {}
    for name in sorted(glob.glob(os.path.join(lexicon_lines.FOLDER, 'L[0-9][0-9].corrected.json'))):
        entries.update((e['headword'], e) for e in outputs.load_json(name)['entries'])
    return entries


# ---- the index the rules are proposed from

def _hits(text, forms):
    text = f" {readings.key(text)} "
    return any(f' {readings.key(f)} ' in text for f in forms if readings.key(f))


def index_rows(book, entries, paired_text, threshold):
    """Per headword: the paragraphs and notes printing one of its spellings, in how many sections, whether a paired
    page names it, and whether that makes it central (paired page, or at least `threshold` places)."""
    rows = []
    for e in entries:
        forms = e['spellings'] + [e['headword']]
        places = [i for i in book.order if _hits(book.texts[i], forms)]
        sections = {book.paragraphs[book.notes[i]['paragraph'] if i in book.notes else i]['section'] for i in places}
        paired = _hits(paired_text, forms)
        rows.append({'headword': e['headword'], 'places': len(places), 'sections': len(sections),
                     'paired_page': paired, 'central': paired or len(places) >= threshold})
    return rows


def _paired_text():
    return '\n'.join(outputs.read(p) for p in sorted(glob.glob(os.path.join(paths.WORK, 'pairs', 'U*.corrected.md'))))


def index():
    book, entries = preface.load(), list(lexicon().values())
    counts = sorted(r['places'] for r in index_rows(book, entries, '', 0))
    threshold = counts[len(counts) // 2]  # recurring: printed at least as often as the median headword
    rows = index_rows(book, entries, _paired_text(), threshold)
    lines = [f"{r['headword']} | spellings: {', '.join(e['spellings'])} | senses: {len(e['senses'])} | places: "
             f"{r['places']} | sections: {r['sections']} | paired page: {'yes' if r['paired_page'] else 'no'} | "
             f"central: {'yes' if r['central'] else 'no'}" for r, e in zip(rows, entries)]
    head = (f'# One line per word-list headword. places: paragraphs and margin notes printing one of its spellings; '
            f'sections: in how many of the 8 sections; central: on a paired page, or at least {threshold} places.\n')
    paths.write(path('index.txt'), head + '\n'.join(sorted(lines, key=str.lower)) + '\n')
    return f"index: {len(rows)} headwords, {sum(r['central'] for r in rows)} central (threshold {threshold} places)"


# ---- the rules

def check_rules(rules, headwords):
    problems, owner, keys = [], {}, {}
    for e in rules['entries']:
        name = e['name']
        problems += [f'{name}: unknown headword {h}' for h in e['headwords'] if h not in headwords]
        for h in e['headwords']:
            if h in owner:
                problems.append(f'{h}: in {owner[h]} and {name}')
            owner.setdefault(h, name)
        if not e['keys']:
            problems.append(f'{name}: no keys')
        if e.get('tier') not in ORDER:
            problems.append(f'{name}: tier')
        if e.get('gated') and not _secondary(rules, e):
            problems.append(f'{name}: gated, but nothing gates it')
        problems += st_world.key_problems(name, e['keys'], rules.get('no_plural', []))
        for k in e['keys']:
            keys.setdefault(k.lower(), []).append(name)
    gated = {k.lower() for e in rules['entries'] if e.get('gated') for k in e['keys']}
    problems += [f'open key not on a gated subject: {k}' for k in rules.get('open_keys', []) if k.lower() not in gated]
    names = [e['name'] for e in rules['entries']]
    problems += [f'subject twice: {n}' for n in sorted({n for n in names if names.count(n) > 1})]
    return problems + [f'key on {len(v)} subjects: {k} ({", ".join(v)})' for k, v in keys.items() if len(v) > 1]


def _build_bundle(name, prompts, inputs, limit=OPUS):
    book = preface.load()
    entry = bundle.build(book, name, prompts, [], inputs, limit, prompt_check.load(book))
    return f"{name}: about {entry['tokens']:,} tokens"


def rules_bundle():
    index()
    return _build_bundle('lorebook_rules', [prompt('lorebook_rules.md')], [('INDEX', path('index.txt'))])


def _entries_text(headwords, lexicon_entries):
    return ''.join(lexicon_page.entry(lexicon_entries[h]) for h in headwords if h in lexicon_entries)


def review_bundle():
    """The proposal, the script's findings on it and the word-list text of every subject that joins headwords."""
    proposal, lex = outputs.load_json(path('rules_proposed.json')), lexicon()
    paths.write(path('rules_findings.txt'), '\n'.join(check_rules(proposal, lex)) or 'none')
    joined = [h for e in proposal['entries'] if len(e['headwords']) > 1 for h in e['headwords']]
    paths.write(path('joined.md'), _entries_text(joined, lex) or 'none')
    return _build_bundle('lorebook_review', [prompt('lorebook_rules.md'), prompt('lorebook_review.md')],
                         [('INDEX', path('index.txt')), ('PROPOSAL', path('rules_proposed.json')),
                          ('SCRIPT FINDINGS', path('rules_findings.txt')), ('JOINED ENTRIES', path('joined.md'))],
                         FABLE)


# ---- content

def batches():
    rules, lex = outputs.load_json(RULES), lexicon()
    cut, size = [[]], 0
    for e in rules['entries']:
        cost = bundle.tokens(_entries_text(e['headwords'], lex))
        if cut[-1] and size + cost > BATCH:
            cut.append([])
            size = 0
        cut[-1].append(e['name'])
        size += cost
    paths.write(path('batches.json'), json.dumps(cut, ensure_ascii=False, indent=0) + '\n')
    return f"{len(rules['entries'])} subjects in {len(cut)} batches"


def _subjects(number):
    names = outputs.load_json(path('batches.json'))[number - 1]
    rules, lex = {e['name']: e for e in outputs.load_json(RULES)['entries']}, lexicon()
    text = ''.join(f"\n# SUBJECT: {n}\n" + _entries_text(rules[n]['headwords'], lex) for n in names)
    paths.write(path(f'subjects_{number:02d}.md'), text.lstrip())
    return path(f'subjects_{number:02d}.md')


def writer(number):
    return _build_bundle(f'lorebook_writer_{number:02d}', [prompt('lorebook_writer.md')],
                         [('SUBJECTS', _subjects(number))])


def blocks(text):
    """{subject: content} of a content page, which ends with the end marker."""
    pieces = re.split(r'(?m)^(?=## )', text.rsplit(END, 1)[0])
    return {p.split('\n')[0][3:].strip(): p.split('\n', 1)[1].strip() for p in pieces if p.startswith('## ')}


def check(number, candidate):
    text = outputs.read(candidate)
    names = outputs.load_json(path('batches.json'))[number - 1]
    merged = {e['name']: len(e['headwords']) > 1 for e in outputs.load_json(RULES)['entries']}
    found = blocks(text)
    problems = [] if text.rstrip().endswith(END) else ['end marker missing']
    problems += [f'subject missing: {n}' for n in names if n not in found]
    problems += [f'subject not asked for: {n}' for n in found if n not in names]
    for name, content in found.items():
        problems += st_world.content_problems(name, content, merged.get(name, False))
    return problems


def checker(number):
    findings = path(f'content_{number:02d}.findings.txt')
    paths.write(findings, '\n'.join(check(number, path(f'content_{number:02d}.md'))) or 'none')
    return _build_bundle(f'lorebook_checker_{number:02d}', [prompt('lorebook_writer.md'),
                         prompt('lorebook_checker.md')], [('SUBJECTS', _subjects(number)),
                         ('CANDIDATE', path(f'content_{number:02d}.md')), ('SCRIPT FINDINGS', findings)])


# ---- the lorebook

def _secondary(rules, e):
    """A gated subject's secondary keys: every distinctive word that is not its own key (the context words, the keys
    of ungated subjects, the open keys of others), then its own open keys, which so fire alone."""
    own, open_keys = {k.lower() for k in e['keys']}, {o.lower() for o in rules.get('open_keys', [])}
    distinctive = (rules.get('context', []) + [k for o in rules['entries'] if not o.get('gated') for k in o['keys']]
                   + rules.get('open_keys', []))
    found = {}
    for k in [k for k in distinctive if k.lower() not in own] + [k for k in e['keys'] if k.lower() in open_keys]:
        found.setdefault(k.lower(), k)
    return list(found.values())


def st_entries(rules, content):
    """The SillyTavern entries: order by tier; a gated subject needs a context word or one of its open keys; only
    ungated core subjects are reached by recursion, and only core content is scanned."""
    base = dict(constant=False, addMemo=True, position=1, delayUntilRecursion=False, probability=100,
                useProbability=False, depth=4, selectiveLogic=0, disable=False)
    out = []
    for e in rules['entries']:
        gated = bool(e.get('gated'))
        secondary = _secondary(rules, e) if gated else []
        out.append(dict(base, key=e['keys'], keysecondary=secondary, selective=gated, order=ORDER[e['tier']],
                        comment=f"{e['name']} (word list: {', '.join(e['headwords'])})", content=content[e['name']],
                        excludeRecursion=gated or e['tier'] != 1, preventRecursion=e['tier'] != 1))
    return out


def build(placeholder=False):
    """The lorebook; with `placeholder` each subject's content is its name, for the trigger test before content."""
    rules = outputs.load_json(RULES)
    problems = check_rules(rules, lexicon())
    if placeholder:
        content = {e['name']: e['name'] for e in rules['entries']}
    else:
        content = {}
        for number in range(1, len(outputs.load_json(path('batches.json'))) + 1):
            content.update(blocks(outputs.read(path(f'content_{number:02d}.corrected.md'))))
        for e in rules['entries']:
            if e['name'] not in content:
                problems.append(f"no content: {e['name']}")
                content[e['name']] = ''
            problems += st_world.content_problems(e['name'], content[e['name']], len(e['headwords']) > 1)
    entries = st_entries(rules, content)
    readme = dict(entries[0] if entries else {}, key=[], keysecondary=[], comment='READ ME', content=README,
                  selective=False, order=0, disable=True)
    book = {'name': 'Croll, Admonitory Preface', 'description': "Subjects of Croll's Admonitory Preface (1657), "
            'as the Preface itself explains them.',
            'entries': {str(uid): dict(e, uid=uid) for uid, e in enumerate([readme] + entries)}}
    if not problems:  # a lorebook with a failure is never written
        paths.write(OUT if not placeholder else path('placeholder.json'),
                    json.dumps(book, ensure_ascii=False, indent=1) + '\n')
    words = [len(e['content'].split()) for e in entries]
    return problems, (f"{len(entries)} entries, {sum(len(e['key']) for e in entries)} keys, "
                      f"{sum(e['selective'] for e in entries)} gated, {sum(words):,} words")


def lines_bundle():
    entries = outputs.load_json(RULES)['entries']
    groups = [(title, [e['name'] for e in entries if e['tier'] == t])
              for t, title in ((1, 'core'), (2, 'secondary'), (3, 'other'))]
    paths.write(path('subject_names.txt'), '\n'.join(f'## {title}\n' + '\n'.join(names) + '\n'
                                                     for title, names in groups))
    return _build_bundle('lorebook_lines', [prompt('lorebook_lines.md')], [('SUBJECT NAMES',
                                                                            path('subject_names.txt'))])


def line_problems(wanted, text, inserted, cut, tier):
    """A test line's failures: a subject it names that is not one, a core or secondary one not inserted."""
    problems = []
    for name in (w.strip() for w in wanted.split(';')):
        if name not in tier:
            problems.append(f'not a subject: {name}: {text}')
        elif name not in inserted and tier[name] < 3:
            problems.append(f"{'cut by budget' if name in cut else 'does not fire'}: {name}: {text}")
    return problems


def trigger_test(built):
    """Each line of trigger_lines.txt is `subject; subject | chat line`, or `- | chat line` for an everyday one."""
    entries = [dict(e, name=e['comment'].split(' (word list')[0]) for e in outputs.load_json(built)['entries'].values()
               if not e['disable']]
    tier = {e['name']: e['tier'] for e in outputs.load_json(RULES)['entries']}
    problems, report, counts = [], [], []
    for row in outputs.read(path('trigger_lines.txt')).splitlines():
        if '|' not in row:
            continue
        wanted, text = (part.strip() for part in row.split('|', 1))
        inserted, cut = st_world.fire(entries, text)
        counts.append(len(inserted) + len(cut))
        report.append(f'{text}\n  in: {", ".join(inserted) or "-"}' + (f'\n  cut: {", ".join(cut)}' if cut else ''))
        if wanted == '-':
            problems += [f'everyday line fires {n}: {text}' for n in inserted + cut]
            continue
        problems += line_problems(wanted, text, inserted, cut, tier)
    paths.write(path('fire_report.txt'), '\n'.join(report + ['', '# Failures'] + problems) + '\n')
    counts.sort()
    return problems, f'{len(counts)} lines, entries per line: median {counts[len(counts) // 2]}, most {counts[-1]}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['index', 'rules', 'review', 'check_rules', 'batches', 'writer', 'checker',
                                         'check', 'build', 'lines', 'fire'])
    parser.add_argument('arg', nargs='?')
    parser.add_argument('--placeholder', action='store_true', help='build or fire with names for content')
    args = parser.parse_args()
    try:
        if args.step == 'check_rules':
            return outputs.report(check_rules(outputs.load_json(args.arg or RULES), lexicon()), 'rules pass')
        if args.step == 'check':
            number = int(re.search(r'content_(\d\d)', args.arg).group(1))
            return outputs.report(check(number, args.arg), 'content passes')
        if args.step in ('build', 'fire'):
            built = path('placeholder.json') if args.placeholder else OUT
            found, summary = build(args.placeholder) if args.step == 'build' else trigger_test(built)
            return outputs.report(found + [summary] if found else [], summary)
        done = {'index': index, 'rules': rules_bundle, 'review': review_bundle, 'batches': batches,
                'lines': lines_bundle, 'writer': lambda: writer(int(args.arg)),
                'checker': lambda: checker(int(args.arg))}[args.step]()
    except bundle.BundleError as error:
        return outputs.report([str(error)], '')
    return outputs.report([], done)


if __name__ == '__main__':
    sys.exit(main())
