# For word-list entries

The page labelled `PAGE` is a JSON object of word-list entries for the headwords labelled `HEADWORDS`. Besides the checks above:
- Each sense: does its evidence show it? Narrow it to what the quotes show; a sense no quote shows is removed.
- `use` is `veiled` only where the text uses the word in a covered or second sense; `reading` is `Stated` only where the text itself says the meaning, `several` only with each reading and its basis.
- `voice` names whose words the evidence quotes.
- Each headword has an entry or stands in `skipped` with its reason; a skipped word the lines use in a sense of the book's own gets an entry.
- `headword` stays the word in today's spelling, `spellings` the book's own.
- The form stays: write the same JSON object, corrected and whole, and nothing else to the file: `entries` (each with `headword`, `spellings`, `senses`; each sense with `sense`, `use`, `reading`, `voice`, `evidence` as a list of `{ref, quote}`), `skipped`, `sections_read`, `end_marker`.
