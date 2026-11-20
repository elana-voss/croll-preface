# Task: settle the units of what the book carries

Your bundle holds the book's lines that a proposal cites, the `MARKING LIST` the proposal was made from (reference | voice | tags, if any | “quote” | what it names), and the `PROPOSAL`. The proposal and the list are earlier outputs: check each point against the book's lines.

The proposal follows these definitions:
- A **process** is a course of operations the book presents as leading to one final result. A different final result is a different process, not a variant. A preparation that serves a process is part of it.
- **What the book carries** is what the book itself presents as the thing it delivers to its reader: a process where it marks one; where it marks none, whatever it marks instead, named in the book's own words.
- A **unit** is one thing the book's own marking sets apart as one. A differently marked thing is a different unit; what serves a unit is part of it. Where the marking sets nothing apart, the book as a whole is the one unit.

## Settle
The question is one only: does the division follow the way the text itself marks what it delivers? Judge the book on its own terms; no other book's form is a model for it.
1. The answer on process: does a cited line present a course of operations leading to a result the book delivers, or does none?
2. Each unit: is it one in the text's marking, or two the text treats as one, or part of another, or no unit at all? Is a marking left out that the text sets apart as one? Is each name and kind the book's words, and each voice right?

Where the lines in your bundle do not settle a point, keep the proposal's ruling and name the point under `open`.

## Output
Write one JSON object to the file your task names, and nothing else to it: the settled division in the proposal's form (`process`, `units`, `left`), then

```json
 "changes": [{"kind": "merge | split | move | not a unit | added | answer | wording", "what": "<unit ids or marking>", "ref": "SEC.4", "quote": "<the line that settles it>", "why": "<short>"}],
 "open": [{"point": "<short>", "ref": "SEC.4"}],
 "sections_read": ["SEC"], "end_marker": "END OF OUTPUT"
```

Run `python scripts/quote_check.py <your file>` and correct until it prints `all quotes pass`. Then reply with one line: the file written, the answer on process, the settled units by id and name, the number of changes.
