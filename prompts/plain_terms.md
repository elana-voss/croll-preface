# Task: one unit of what the book carries, in Plain Terms

Your bundle holds the book's lines this unit draws on and three earlier outputs: `DIVISION`, the settled answer on whether the book marks a process, with its basis; `UNIT`, this unit's settled entry (its name and kind in the book's words, the lines that mark it, its parts); and `CANDIDATES`, the readers' observations on these lines, one per line: reference | kind | voice | tags, if any | “quote” | what it names, if given | note (a note ending in … is cut short). They help you find things; they are not proof. Use one only where you see it in the text yourself, and cite the text.

Write one page: everything the given lines say about this unit, with its evidence, for a reader who wants to check each point. The length follows from what the text supports, at most about 4,000 words; there is no target. If the text supports only a little, the page is short.

## The page
1. `# <the unit's name, in modern spelling> in Plain Terms`.
2. One short paragraph: what the page covers, where in the book the unit stands, and what the four marks below mean.
3. `## Process or not`: the division's answer, given as the finding of the division made from the readings of the whole Preface, with its basis quoted and referenced. Where the answer is no, say what the book carries instead, in its own words. Never word the answer as something the book says of itself.
4. `## In brief`: a numbered list of the main points, each opening with its mark and ending with its reference.
5. Then one `##` sub-heading for each thing the text says about the unit, in the text's order and under its own heads where it gives them: never in an order or under kinds you bring to it.
6. `## Key terms and open questions`, last: a table under the header `| Term | Status | Plain or veiled |`, one row per term the page relies on, the status `Stated`, `Interpreted`, `Several defensible readings` or `Plain` as the page finds it, the last column `veiled` where the page finds the book uses the term for something other than what it plainly names, else `plain`; no quotes and no references in the table. Then `### Open questions`: points where the given lines allow more than one reading, or where the author says he withholds or covers something, each with its reference.

## Points
Each point is one paragraph that opens with its mark and ends with its reference.
- `**Stated.**` the text says this outright.
- `**Interpreted.**` your inference, worded as yours, with the passages it rests on, and the narrowest reading they support.
- `**Several readings.**` each reading with its basis.
- `**Plain.**` the words mean what they plainly say, with no sign in the text of another sense.

Keep the voices apart: where the words are someone else's, say whose; what the author rejects is not his. A quote is set in curly quotation marks, “like this”, with its reference bracket after it in the same paragraph, `[SEC.12]`. No straight quotation marks (`"`) anywhere. No words from outside the book: where the book has its own word for a thing, use it and explain it from the text.

Write the page to the file your task names, ending with the closing lines. Run `python scripts/quote_check.py <your file>` and correct until it prints `all quotes pass`. Then reply with one line: the file written and its word count.
