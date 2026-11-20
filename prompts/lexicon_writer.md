# Task: write word-list entries

Your bundle holds the headwords labelled `HEADWORDS`, one per line, a word's spellings joined by ` / `; the book's lines where they stand; and the joined readings that mention it labelled `UNVERIFIED CANDIDATE`. Write one entry per headword, from these lines only. Note each headword's references as you read; your first reading will not stay with you to the end.

## Each entry
- `headword`: the word in modern spelling; `spellings`: the book's own spellings as they stand in the lines given.
- `senses`: each sense the word has in this book, one per sense the lines show. For each: `sense` (in plain words), `use` (`plain` where the word means what it ordinarily means, `veiled` where the text uses it in a covered or second sense), `reading` (`Stated`, `Interpreted` or `several`, by the rule for reading what is hidden; for `several`, each reading with its basis), `voice`, and `evidence`: a list of `{ref, quote}`, at least one, each quote word for word.
- Give the narrowest sense the lines support. A sense no quote shows is left out.
- No words from outside the book.
- A headword the lines show only in the everyday sense of a common word, with nothing the book marks in it, gets no entry: name it in `skipped`, as `{headword, why}`, why in one line.

## Output
Write one JSON object to the file your task names, and nothing else to it:

```json
{"entries": [{"headword": "<modern>", "spellings": ["<as printed>"], "senses": [{"sense": "<plain words>", "use": "plain", "reading": "Stated", "voice": "CROLL", "evidence": [{"ref": "SEC.4", "quote": "<words as they stand>"}]}]}],
 "skipped": [{"headword": "<modern>", "why": "<one line>"}],
 "sections_read": ["SEC"], "end_marker": "END OF OUTPUT"}
```

Then reply with one line: the file written, the number of entries and the number skipped.
