# Task: propose the units of what the book carries

Your bundle holds the heads of the book's sections and, labelled `MARKING LIST`, every place where readers found the text naming, heading, numbering or announcing something as one. Each line: reference | voice | tags, if any | “quote” | what it names. The list is an earlier output: its lines are candidates, and their quotes stand in the book as given.

## Definitions
- A **process** is a course of operations the book presents as leading to one final result. A different final result is a different process, not a variant. A preparation that serves a process is part of it.
- **What the book carries** is what the book itself presents as the thing it delivers to its reader: a process where it marks one; where it marks none, whatever it marks instead. Its kind is not set beforehand: name it in the book's own words.
- A **unit** is one thing the book's own marking sets apart as one. A differently marked thing is a different unit; what serves a unit is part of it. Where the marking sets nothing apart, the book as a whole is the one unit.

## Two questions, in this order
1. Does the book mark a process? A thing the author names, praises or promises is not a process unless the text presents a course of operations leading to it. Answer yes or no, with the marking lines that show it.
2. The units: the processes, if the book marks any; else what the marking list shows the book carries instead. Never sort the book into kinds you bring to it.

What the author reports in order to reject it is not what the book carries. A head that only divides the argument is not a unit by itself.

## Output
Write one JSON object to the file your task names, and nothing else to it:

```json
{"process": {"answer": "no", "basis": [{"ref": "SEC.4", "quote": "<words as they stand>", "why": "<short>"}]},
 "units": [{"id": "U1", "name": "<the book's words>", "kind": "<in the book's words>", "voice": "CROLL",
   "marked_at": [{"ref": "SEC.4", "quote": "<the words that set it apart as one>"}],
   "parts": [{"ref": "SEC.9", "quote": "<a marking that serves it>", "why": "<short>"}],
   "why_one": "<what in the marking makes it one unit, not part of another>"}],
 "left": [{"ref": "SEC.12", "quote": "<words as they stand>", "why": "<why it is no unit of its own>"}],
 "sections_read": ["SEC"], "end_marker": "END OF OUTPUT"}
```

List under `left` each marking a reader could take for a unit of its own, and only those. Copy every quote from the marking list or the heads. Run `python scripts/quote_check.py <your file>` and correct until it prints `all quotes pass`. Then reply with one line: the file written, the answer on process, the units by id and name.
