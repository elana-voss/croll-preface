"""The one normalising function and what rests on it: words and quote matching.

Extracted text carries three kinds of editorial marks, all outside the book's words:
note anchors `[N012]`, gaps `{G012: 2 letters illegible}` and printed numerals `{No. IV}`.
"""
import re
import unicodedata

NOTE_ANCHOR = re.compile(r'\[N\d+\]')
GAP_MARK = re.compile(r'\{G\d+:[^}]*\}')
NUMERAL = re.compile(r'\{No\. [IVXLC]+\}')
ANY_BRACES = re.compile(r'\{[^}]*\}')
LINE_END_HYPHEN = re.compile(r'-[ \t]*\r?\n\s*')
FOLD = str.maketrans({'ſ': 's', 'Ʋ': 'v', 'ʋ': 'v', 'æ': 'ae', 'œ': 'oe'})
WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*|&")  # an apostrophe inside a word, and '&' for 'and'
GAP_SIGN = '\x01'


def normalise(text):
    """Long s and other letter forms folded, accents and abbreviation strokes dropped,
    words broken at a line end joined, whitespace collapsed, lower case."""
    text = LINE_END_HYPHEN.sub('', text)
    text = unicodedata.normalize('NFKD', text.translate(FOLD))
    text = ''.join(c for c in text if not unicodedata.combining(c)).translate(FOLD)
    return re.sub(r'\s+', ' ', text).strip().lower()


def printed(text):
    """The book's text alone: every editorial mark removed, nothing put in its place."""
    return NUMERAL.sub('', GAP_MARK.sub('', NOTE_ANCHOR.sub('', text)))


def words(text):
    """Normalised words; a note anchor separates words, a gap inside a word does not."""
    text = NUMERAL.sub(' ', GAP_MARK.sub('', NOTE_ANCHOR.sub(' ', text)))
    return WORD.findall(normalise(text))


def key(word):
    """A word's comparison form."""
    return ''.join(WORD.findall(normalise(word)))


def _matchable(text, is_quote):
    text = NUMERAL.sub(' ', text)
    return normalise((ANY_BRACES if is_quote else GAP_MARK).sub(GAP_SIGN, text))


def find_quote(quote, text):
    """True if the quote stands in the text as whole words, a gap written in the quote as any {…}.

    A quote may not run across a note anchor: each stretch between anchors is searched alone.
    """
    wanted = _matchable(quote, True)
    whole = re.compile(r'(?<![^\W_])' + re.escape(wanted) + r'(?![^\W_])')  # begins and ends on whole words
    return bool(wanted) and any(whole.search(_matchable(part, False)) for part in NOTE_ANCHOR.split(text))
