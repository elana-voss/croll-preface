"""Reading chunks: each section cut at paragraphs into the fewest near-equal chunks under a cap."""
import math

MAX_WORDS = 4200


def _split(items, count):
    """Cut at the paragraph boundaries nearest to `count` equal shares."""
    total = sum(words for _, words in items)
    pieces, current, done = [], [], 0
    for index, (pid, words) in enumerate(items):
        current.append((pid, words))
        done += words
        following = items[index + 1][1] if index + 1 < len(items) else None
        target = total * (len(pieces) + 1) / count
        if following is not None and len(pieces) < count - 1 and abs(done - target) <= abs(done + following - target):
            pieces.append(current)
            current = []
    return pieces + [current]


def build(paragraphs, max_words=MAX_WORDS):
    """paragraphs: (section, paragraph id, words) in reading order. A paragraph over the cap stays whole."""
    sections = {}
    for section, pid, words in paragraphs:
        sections.setdefault(section, []).append((pid, words))
    table = []
    for section, items in sections.items():
        count = math.ceil(sum(words for _, words in items) / max_words)
        pieces = _split(items, count)
        while count < len(items) and any(sum(w for _, w in p) > max_words and len(p) > 1 for p in pieces):
            count += 1
            pieces = _split(items, count)
        for number, piece in enumerate(pieces, 1):
            table.append({'id': f'{section}-{number}', 'section': section, 'first': piece[0][0],
                          'last': piece[-1][0], 'paragraphs': len(piece), 'words': sum(w for _, w in piece)})
    return table
