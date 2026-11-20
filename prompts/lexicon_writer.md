# Task: write word-list entries

Your bundle holds, for each headword your task names, the book's lines where it stands, and the joined readings that mention it labelled `UNVERIFIED CANDIDATE`. Write one entry per headword, from these lines only.

## Each entry
- `headword`: the word in modern spelling; `spellings`: the book's own spellings as they stand in the lines given.
- `senses`: each sense the word has in this book, one per sense the lines show. For each: `sense` (in plain words), `use` (`plain` where the word means what it ordinarily means, `veiled` where the text uses it in a covered or second sense), `reading` (`Stated`, `Interpreted` or `several`, by the rule for reading what is hidden; for `several`, each reading with its basis), `voice`, and `evidence`: a list of `{ref, quote}`, at least one, each quote word for word.
- Give the narrowest sense the lines support. A sense no quote shows is left out.
- No words from outside the book.

## Output
Write one JSON object to the file your task names, and nothing else to it:

```json
{"entries": [{"headword": "<modern>", "spellings": ["<as printed>"], "senses": [{"sense": "<plain words>", "use": "plain", "reading": "Stated", "voice": "CROLL", "evidence": [{"ref": "SEC.4", "quote": "<words as they stand>"}]}]}],
 "sections_read": ["SEC"], "end_marker": "END OF OUTPUT"}
```

Then reply with one line: the file written and the number of entries.
