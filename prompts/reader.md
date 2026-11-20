# Task: read closely and record what the text shows

Read every paragraph and every margin note of the book's text in your bundle, in order, and record observations. Another reader reads the same text on their own; a later step joins both readings. Record; do not judge. You give no verdict on what the book is about, what it hides or what it delivers.

## What to record
Each observation is one item of one of these kinds:

- `marking`: the text names, heads, numbers or announces something as one thing (a work, an operation, a result, or anything else it sets apart). Field `what`: the thing, in the book's own words.
- `own definition`: the text says what one of its words or names means.
- `concealment`: the text says something is hidden, covered, withheld, or meant for some readers only.
- `local signal`: a turn of phrase in the text that points to a second sense here (for example a word the text itself says is not meant plainly).
- `operation`: a concrete step of work the text describes (what is done, to what, how).
- `position`: a view the author states as his own. One item per view.
- `voice`: words the text gives to a named person, writing or group. Field `name`: the name as the book spells it.
- `cross-reference`: the text points to another place in this writing or to another writing of the author.
- `internal conflict`: the text says something that does not agree with another passage you were given. Field `with`: the other reference.

Every item has `n` (1, 2, 3 … in reading order), `ref`, `type`, `quote`, and a short `note` in plain words saying what the quote shows. Add `term` where the item turns on one word or name of the book that a word list of this book should hold (the book's spelling). Add `tags` (`note-only`, `wording-dependent`) where they apply.

Cover the whole text given: the end of the bundle counts as much as its start. Record what you find; there is no target count. A margin note naming a person or writing beside a passage is a `voice` item for that passage.

## Output
Write one JSON object to the file your task names, and nothing else to it:

```json
{"items": [{"n": 1, "ref": "SEC.4", "type": "marking", "quote": "<words as they stand>", "what": "<the thing, in the book's words>", "note": "<what it shows>"}],
 "sections_read": ["SEC"], "end_marker": "END OF OUTPUT"}
```

Then reply with one line: the file written and the number of items.
