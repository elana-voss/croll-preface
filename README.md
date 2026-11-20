# Croll's Admonitory Preface — A Reading

A close reading, in English, of Oswald Croll's *Admonitory Preface* as printed in *Philosophy Reformed & Improved in Four Profound Tractates* (London 1657, Englished by H. Pinnell): from its title to the end of its sixth chapter. The book is the only source; nothing from outside it enters the pages.

## What is here

- `src/`: the site, an [mdBook](https://rust-lang.github.io/mdBook/): one page per section of the Preface, a page on the Preface as a whole, two subjects each on a *Plain Terms* page (every point with its quotes and references) and a *Plain Language* page (the same in everyday words), and a word list. `src/introduction.md` explains the references.
- `lorebook/Croll_Admonitory_Preface.json`: a SillyTavern World Info file (lorebook) built from the word list: 75 entries that give a chat model what the Preface says about a subject when a chat names it. Subjects named by everyday words fire only beside a distinctive word of the book.
- `text/preface.json`: the Preface extracted by script from the transcription, with the paragraph and margin-note ids that every reference uses.
- `sources/A74670.xml`: the transcription.
- `scripts/`, `prompts/`, `tests/`: the extraction, the checks and the prompts the pages were made with; `work/`: the intermediate readings and drafts.

## Build

With Python 3 and mdBook installed:

```
python -m unittest discover -s tests
python scripts/publish.py
```

`publish.py` turns the finished pages in `work/` into `src/`, checks them (rights, links, no references on the Plain Language pages) and runs `mdbook build`; the site is written to `book/`.

## Text and rights

The transcription is the Text Creation Partnership's keyed edition of the 1657 printing (EEBO-TCP Phase 2, A74670). The TCP has waived all copyright and related rights to it under the [CC0 1.0 Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/). The 1657 printing is in the public domain. No page images are included. See `RIGHTS.md`.
