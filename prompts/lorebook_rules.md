# Task: the subjects and keys of a chat lorebook

A lorebook is a set of short background texts for a chat program. When one of an entry's keys appears in the recent chat, the program puts that entry's text into the model's prompt, so that a character who speaks about this book speaks in line with it. Keys match whole words, without regard to case, with no plural or stem handling: every form a user would type must be a key. A key can be a regular expression written `/<pattern>/i`. A key holds no comma.

Your bundle has no book text. It holds `INDEX`: one line per headword of the project's checked word list, with the book's spellings, how many senses the list gives it, at how many places and in how many of the book's sections one of its spellings is printed, whether a page on one of the book's two main units names it, and whether that makes it central.

## The subjects
- A subject is something a person in a chat thinks of as one thing. Only central headwords become subjects. A headword that is not central may be folded into a central subject when its name shows it is a kind, part or form of that subject; otherwise it is left out.
- Join headwords into one subject only where their names show they are spellings, forms or names of one thing; a reviewer checks every join against the word list itself.
- Leave out persons and writings a chat about the book would not name, everyday words with nothing of the book's own in them, and phrases nobody types.
- The size guide: tens of subjects, not hundreds.

## The fields of a subject
- `name`: the subject in today's spelling, as a reader would name it.
- `headwords`: the index headwords it holds, exactly as the index spells them.
- `keys`: the words and short phrases a person would type in a chat today: the term in today's spelling, the book's own spelling where a user might type it, and every plural or other form (or one regular expression for them). No titles, sentences, articles, brackets, or a headword with a qualifier. A synonym from today's language only where it is a plain spelling change of the book's word. Usually one to four keys. No key on two subjects.
- `tier`: 1 for the core (named on a unit page and printed at many places), 2 for the secondary, 3 for the rest.
- `gated`: true where a key is an everyday word that ordinary chat would hold, so that the subject is inserted only when a context word or one of its own open keys stands beside it. The author's own subject, if there is one, is gated too, since a character named after him would insert it every turn.

## The fields of the whole
- `context`: 15 to 30 words that mark a chat about this book's subjects and nothing else, in today's spelling, none of them an everyday word. A gated subject is inserted when one of them stands beside its key.
- `open_keys`: keys of gated subjects distinctive enough to insert the subject alone.
- `no_plural`: keys that take no plural (names, adjectives, words used only in the singular); every other key needs its plural among the subject's keys.

## Output
Write one JSON object to the file your task names, and nothing else to the file: `entries` (a list of subjects, each `{name, headwords, keys, tier, gated}`), `context`, `open_keys`, `no_plural`, `end_marker` (`"END OF OUTPUT"`), last. Then run `python scripts/lorebook.py check_rules <your file>` from the project folder and correct until it prints `rules pass`. Reply with one line: the file written, the number of subjects, the number gated.
