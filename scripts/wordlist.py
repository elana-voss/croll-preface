"""A plain-English word list read from a spell file already on this machine (Vim's .spl)."""
import argparse
import struct

import paths

MAGIC = b'VIMspell'
SECTION_END = 255
BY_NOFLAGS, BY_INDEX, BY_FLAGS, BY_FLAGS2 = 0, 1, 2, 3
WF_REGION, WF_AFX = 0x01, 0x20
NOT_PLAIN = 0x02 | 0x04 | 0x08 | 0x10 | 0x40 | 0x80  # capitalised, rare or banned entries


def _skip_sections(data):
    if not data.startswith(MAGIC):
        raise ValueError('not a Vim spell file')
    at = len(MAGIC) + 1
    while data[at] != SECTION_END:
        at += 6 + struct.unpack('>I', data[at + 2:at + 6])[0]
    return at + 1


class _Tree:
    def __init__(self, data, at):
        self.data, self.at = data, at + 4
        size = struct.unpack('>I', data[at:at + 4])[0]
        self.bytes, self.links = [0] * size, [0] * size
        self.read_node(0)

    def _next(self):
        self.at += 1
        return self.data[self.at - 1]

    def _end_of_word(self, marker):
        flags = self._next()
        if marker == BY_FLAGS2:
            self._next()
        if flags & WF_REGION:
            self._next()
        if flags & WF_AFX:
            self._next()
        return flags

    def read_node(self, start):
        """Read one node and, after it, the children it does not share."""
        count = self._next()
        self.bytes[start] = count
        shared = set()
        for slot in range(start + 1, start + count + 1):
            value = self._next()
            if value == BY_INDEX:
                self.links[slot] = int.from_bytes(self.data[self.at:self.at + 3], 'big')
                self.at += 3
                shared.add(slot)
                value = self._next()
            elif value == BY_NOFLAGS:
                value = 0
            elif value in (BY_FLAGS, BY_FLAGS2):
                self.links[slot] = self._end_of_word(value)
                value = 0
            self.bytes[slot] = value
        end = start + count + 1
        for slot in range(start + 1, start + count + 1):
            if self.bytes[slot] and slot not in shared:
                self.links[slot] = end
                end = self.read_node(end)
        return end

    def words(self, node=0, prefix=b''):
        for slot in range(node + 1, node + self.bytes[node] + 1):
            value = self.bytes[slot]
            if value:
                yield from self.words(self.links[slot], prefix + bytes([value]))
            elif not self.links[slot] & NOT_PLAIN:
                yield prefix


def parse(data):
    """The plain lower-case alphabetic words of the file's main word tree."""
    words = set()
    for raw in _Tree(data, _skip_sections(data)).words():
        word = raw.decode('utf-8', 'replace')
        if word.isalpha() and word.islower():
            words.add(word)
    return words


def list_path():
    return paths.PLAIN_ENGLISH


def load():
    with open(list_path(), encoding='utf-8') as f:
        return set(f.read().split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spell_file')
    args = parser.parse_args()
    with open(args.spell_file, 'rb') as f:
        words = parse(f.read())
    paths.write(list_path(), '\n'.join(sorted(words)) + '\n')
    print(len(words), 'words')


if __name__ == '__main__':
    main()
