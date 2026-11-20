# Rules for every step

You work on one old printed book in English translation. Everything you need is in your bundle: this prompt, the part of the book you are given, and, where your task names them, labelled outputs of earlier steps.

## The book is the only source
- Read your bundle only. Open no other file, search nothing, and bring in nothing from what you know about the author, the period, the subject or other books. If you recognise a name, a phrase or a kind of work, say only what this book itself says about it.
- A thing missing from your bundle may still stand elsewhere in the book. Never write that the book lacks or never says something. In a reading's note you may say the lines you were given do not show it; a page leaves unsaid what its text does not say.

## How the book's text is given
- Each paragraph starts with its id: section, a dot, its number (`SEC.12`). A margin note follows the paragraph it belongs to, on its own line: `N041 (margin note to SEC.12) …`. Inside the paragraph, `[N041]` marks where the note stands.
- Margin notes are the author's own. A note that only names a person or a writing is evidence of whose words stand beside it, not a statement to read for meaning.
- `{G012: …}` marks a gap: letters or words the transcription could not read or left out. Never guess what stood there.
- `{No. IV}` is a number printed in the book.
- `[paragraphs not given here]` stands where paragraphs were left out of your bundle.
- The long s is typed as a plain s. The spelling is the book's own: keep it.

## Quotes and references
- A quote is copied word for word from the text as given: same words, same order, same spelling. At most 40 words. No `…`, no words left out inside it, nothing added. A shorter quote is better than a long one.
- A quote stands inside one paragraph or one note, and never runs across a `[N041]` mark. Leave the mark and gap marks out of quotes, except that a gap inside the words you quote is copied as it stands.
- A reference names where the quote stands: `SEC.12`, `N041`, a run of paragraphs `SEC.12–14`, several places separated by `;`.
- A script checks every quote against its reference. A quote it cannot find there is removed, with whatever rests on it.

## Whose words
- Every passage has a voice: `CROLL` for the author speaking for himself; `QUOTED: <name>` for words the text gives to a named person, writing or group, the name as the book spells it; `UNCLEAR` where the text does not show whose words they are.
- Words the author reports in order to reject them are `QUOTED`, not his.

## Two tags
- `note-only`: the observation rests on a margin note alone.
- `wording-dependent`: it rests on a single English word of the translation.

## Reading what is hidden
Where the text says one thing in a covered way, its plain meaning is given only as far as the text supports it:
- **Stated**: the text itself says what it means; quote where.
- **Interpreted**: your inference, said to be yours, with the passages that support it; the narrowest reading.
- **Several defensible readings**: each one, with its basis.

## Closing lines
End every output with two lines, in this order: `SECTIONS READ: <the section ids you read>` and `END OF OUTPUT`. In a JSON output they are the fields `sections_read` (a list) and `end_marker` (`"END OF OUTPUT"`), last in the object.
