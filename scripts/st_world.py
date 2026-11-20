"""SillyTavern World Info as the lorebook rules (LOREBOOK.md) describe it: how a key matches, which entries a chat
line inserts within the budget, and the failure checks on keys and content."""
import re

BUDGET = 2048  # a typical setting: 25 % of an 8,192-token context
ARTICLE = re.compile(r'(?:the|a|an)\s', re.I)
REFERENCE = re.compile(r'¶|\[[^\]]*\]|\b(?:OPEN|MICRO|CH\d)\.\d|\bN\d{3}\b')
LABEL = re.compile(r'(?-i:\b(?:Stated|Interpreted|Veiled|Plain|Voice|Quoted):)|\b(?:our reading|sense \d|the text|'
                   r'the author|(?-i:[Tt]he book)|the Preface|treatise|chapter|margin note|note-only|wording-dependent'
                   r')\b', re.I)
WORDS = (30, 160)  # about 40-150 words (LOREBOOK.md)
MERGED_WORDS = 220  # a subject that folds several word-list entries into one


def is_regex(key):
    return key.startswith('/') and key.rfind('/') > 0


def st_match(key, text):
    """SillyTavern's default matching: case-insensitive; a one-word key as a whole word (JS \\W, ASCII), a key of
    several words anywhere in the text, a regex key as written."""
    if is_regex(key):
        end = key.rfind('/')
        return re.search(key[1:end], text, re.I if 'i' in key[end + 1:] else 0) is not None
    if len(key.split()) > 1:
        return key.lower() in text.lower()
    return re.search(r'(?:^|\W)' + re.escape(key.lower()) + r'(?:$|\W)', text.lower(), re.A) is not None


def _fires(entry, text):
    return (any(st_match(k, text) for k in entry['key'])
            and (not entry['selective'] or not entry['keysecondary']
                 or any(st_match(k, text) for k in entry['keysecondary'])))


def fire(entries, text, budget=BUDGET, steps=1):
    """(inserted, cut) entry names for a chat line: direct matches by order, then `steps` levels of recursion
    (Max Recursion Steps 2 in SillyTavern counts the first scan), each scanning the chat and the inserted content
    (an entry with preventRecursion is not scanned, one with excludeRecursion is not reached); once the token budget
    is spent nothing more goes in."""
    found = sorted((e for e in entries if _fires(e, text)), key=lambda e: -e['order'])
    for _ in range(steps):
        scan = ' '.join([text] + [e['content'] for e in found if not e['preventRecursion']])
        more = sorted((e for e in entries if e not in found and not e['excludeRecursion'] and _fires(e, scan)),
                      key=lambda e: -e['order'])
        if not more:
            break
        found += more
    inserted, cut, used = [], [], 0
    for e in found:
        used += round(len(e['content']) / 4)
        (cut if cut or used > budget else inserted).append(e['name'])
    return inserted, cut


def _plural(key):
    words = key.split()
    last = words[-1]
    if re.search(r'is$', last, re.I):
        last = last[:-2] + 'es'
    elif re.search(r'(?:ss|us)$', last, re.I):
        last += 'es'
    elif last.lower().endswith('s'):
        return None
    elif re.search(r'(?:x|z|ch|sh)$', last, re.I):
        last += 'es'
    elif re.search(r'[^aeiou]y$', last, re.I):
        last = last[:-1] + 'ies'
    else:
        last += 's'
    return ' '.join(words[:-1] + [last])


def key_problems(name, keys, no_plural=()):
    """One entry's keys against LOREBOOK.md; the plural is asked only of keys that pass the rest."""
    problems, lowered = [], {k.lower() for k in no_plural}
    problems += [f'{name}: empty key' for k in keys if not k.strip()]
    for k in (k for k in keys if k.strip() and not is_regex(k)):
        found = [f'{name}: {text}: {k}' for text, bad in (
            ('key starts with an article', ARTICLE.match(k)), ('comma in key', ',' in k),
            ('key over four words', len(k.split()) > 4),
            ('key holds a shorter key', any(len(s) < len(k) and st_match(s, k) for s in keys if s != k))) if bad]
        plural = _plural(k)
        if not found and k.lower() not in lowered and plural and not any(st_match(s, plural) for s in keys):
            found.append(f'{name}: no plural for: {k}')
        problems += found
    return problems


def content_problems(name, text, merged=False):
    problems = [f'{name}: {label}' for label, pattern in (('reference', REFERENCE), ('label', LABEL))
                if pattern.search(text)]
    if re.search(r'\d', REFERENCE.sub('', text)):  # a dose or quantity
        problems.append(f'{name}: digit')
    words = len(text.split())
    if words < WORDS[0] or words > (MERGED_WORDS if merged else WORDS[1]):
        problems.append(f'{name}: {words} words')
    return problems
