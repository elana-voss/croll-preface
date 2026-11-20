# Task: the texts of a chat lorebook

A lorebook is a set of short background texts for a chat program: when a chat names a subject, its text goes into the model's prompt, so that a character speaks in line with this book. Your bundle has no book text. It holds `SUBJECTS`: for each subject, `# SUBJECT: <name>` and the project's checked word-list entries it is made from. Each entry gives the headword, the book's spellings and its senses; each sense is marked *plain* or *veiled* (used in a covered or second sense), *Stated* (the book says the meaning), *Interpreted* (the project's reading) or *several*, with whose words it rests on (`CROLL` is the author; `QUOTED: <name>` a voice he reports; `UNCLEAR`) and the quotes that show it.

## The text of a subject
- Plain prose that stands alone, written as background a model can use in a conversation; the most important point first; 40 to 150 words, up to 220 for a subject made from several entries.
- Only what the entries say: no fact, name, date or reason they do not give, and nothing from what you know of the author, the period or the subject.
- A covered sense is said plainly, beside the plain sense where that also holds, with no mark of which it is. A reading the entries give as the project's own is said as a likelihood (`seems`, `is taken to`), never as certain.
- A view the entries give to a reported voice is said as that person's view, by name, or left out; never as the author's own.
- Several entries in one subject: one connected text, the lesser ones as a short list or clause inside it.
- None of these: references or ids, brackets, marks or labels (`Stated`, `plain`, `voice`), the words "the text", "the book", "the author", "the Preface", "chapter", "margin note", "our reading"; numbers in figures; doses, quantities or steps of a preparation given as fact (say in general what the entries say a preparation is for).
- Today's spelling in your own words; a book spelling only inside a quote, and quote rarely, in curly quotation marks.

## Output
Write to the file your task names, for each subject in its order: a line `## <name>` (the name exactly as given), a blank line, the text. End the file with a line `END OF OUTPUT`. Then run `python scripts/lorebook.py check <your file>` from the project folder and correct until it prints `content passes`. Reply with one line: the file written and the number of subjects.
