# Task: join two readings and rule each passage's voice

Your bundle holds the book's text and two readings of it, labelled `READER A` and `READER B`, made on their own by two readers. Their items are candidates, not facts: check each against the text.

## Join
- Name each reader's items by letter and number: `A3` is item 3 of reader A.
- Where both readers record the same thing, keep one observation and list both sources in `from`. An observation found by one reader only lists that one.
- Keep an item if its quote stands at its reference and the text shows what its kind says. Correct its kind, reference, quote or fields where the text shows they are wrong.
- Drop an item that the text does not bear out, that only repeats another, or whose quote does not stand in the text. Every reader item is either in the `from` of a kept observation or in `dropped`, with a short reason.
- Add nothing of your own beyond what the two readings hold, except in `voices`.

## Rule the voices
Go through the whole text given and list every stretch whose voice is not `CROLL`: words given to a named person, writing or group (`QUOTED: <name>`), or words whose speaker the text does not show (`UNCLEAR`). Each with `ref`, `voice`, a short `quote` that marks where it starts, and `basis`: what in the text shows the voice (a name, a margin note, a verb of saying). Set each kept observation's `voice` by this ruling.

## Output
Write one JSON object to the file your task names, and nothing else to it:

```json
{"observations": [{"ref": "SEC.4", "type": "marking", "quote": "<words as they stand>", "what": "<in the book's words>", "term": "<optional>", "voice": "CROLL", "tags": [], "from": ["A3", "B5"], "note": "<what it shows>"}],
 "dropped": [{"from": "B2", "reason": "<short>"}],
 "voices": [{"ref": "SEC.7", "voice": "QUOTED: <name>", "quote": "<where it starts>", "basis": "<short>"}],
 "sections_read": ["SEC"], "end_marker": "END OF OUTPUT"}
```

Keep the fields `name`, `with` and `what` where the kind has them. Then reply with one line: the file written, observations kept, items dropped.
