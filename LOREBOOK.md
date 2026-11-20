# Lorebook (SillyTavern World Info): rules for this project

Binding for the lorebook step. Written 2026-11-18 from the SillyTavern World Info documentation (<https://docs.sillytavern.app/usage/core-concepts/worldinfo/>) and from what went wrong in the two earlier lorebooks of this series. Examples use placeholders (`<Term>`, `<Synonym>`) on purpose: no subject list or identity is given here.

## 1. What a lorebook entry is (and is not)
- An entry is a piece of background text that SillyTavern **inserts into the model's prompt** when one of its keys appears in the recent chat messages. Its only job: when a chat mentions a subject, give the model what this book says about it, so the character speaks in line with the book.
- It is **not a dictionary**. The lexicon (mdBook page) keeps every term, person and work with references. The lorebook is a separate, much smaller product built from the lexicon.
- An entry belongs in the lorebook only if (a) a normal chat about this book's subjects will actually contain one of its keys, and (b) its content changes what the model says.

## 2. How SillyTavern triggers and inserts (from the documentation)
- **Scan:** only the last N chat messages are scanned (Scan Depth, set by the user; entries can override it). **Speaker names are included in the scan by default.**
- **Matching:** keys are case-insensitive by default. "Match whole words" is on by default: a one-word key matches only a whole word. **There is no plural or stem handling**: every form a user would type must be a key, or a regex key (`/<term>s?/i`). Plain keys cannot contain commas.
- **Secondary keys:** optional filter with AND ANY / AND ALL / NOT ANY / NOT ALL; used to gate entries whose key is an everyday word.
- **Recursion:** if Recursive Scan is on, an inserted entry's content can trigger other entries. Per entry: non-recursable, prevent further recursion, delay until recursion.
- **Budget:** a token budget (percentage of context or fixed). When it is exhausted, **no further entries are inserted, even if their keys match**. Constant entries go first, then higher Order; entries triggered directly beat entries triggered by recursion.
- **What is inserted:** only `content`. Title/memo (`comment`) and keys are never sent to the model.

## 3. Rules
**Selection (thinning out):**
- Candidates come from the lexicon kinds (term, person, work, place, preparation …). Keep an entry only if its subject is **central**: it is cited on a paired page, or it recurs across the book (threshold set by script from reference counts, settled by a Fable reviewer: owner, 2026-11-20).
- Leave out persons, works and phrases cited once or twice, bibliographic references, single preparations or recipes, and rare phrasings nobody types. They stay in the lexicon.
- Size guide: tens to low hundreds of entries. Anti-pattern from earlier lorebooks: well over a thousand entries, most with one obscure multi-word key, and many minor persons nobody mentions in a chat.

**Combining:**
- One entry per subject a user thinks of as one thing: the book's alternative names and spelling variants of one subject become one entry with all their keys (`<Term>`, `<Synonym>`), **only where the book itself identifies them**.
- Fine-grained lexicon entries fold into the parent a user would type (e.g. several kinds of one thing become a short list inside that thing's entry).
- Merging is decided as data (`scripts/lorebook_rules.json`), applied by script, settled by the same reviewer.

**Keys:**
- Words and short phrases a person would actually type in a modern chat: the common term in **modern spelling**, the book's own term if a user might type it, spelling variants, and every plural or inflected form (or a regex key).
- A modern synonym is a key only when the book itself identifies it with the subject, or it is a plain spelling modernisation.
- No long titles, sentences, phrases with articles or brackets, or headword-with-qualifier strings. Typically 1–4 keys; more only for genuine variants.
- Everyday words as the main key: gate with a short, topical secondary-key list (AND ANY).
- The author's own entry is gated too (a character named after the author would otherwise fire it every turn through the speaker-name scan).
- Bias toward triggering when the subject is genuinely mentioned (owner's standing decision); no triggers on ordinary chat.

**Content ("clean"):**
- Plain prose, standalone, written as knowledge the model can use in a conversation; most important point first; about 40–150 words.
- No references, no entry ids, no labels such as `[Term: …]`, `Stated:`, `Interpreted:`, no "the text says / the author records / the book", no provenance (treatise, voice) — provenance goes in `comment` and the lexicon.
- Where the book gives a term a veiled sense (Stated or Interpreted, see the reading rule in PLAN.md), the content states it plainly, beside the plain sense where that also holds, without meta-labels. Terms the book uses plainly: the plain sense only.
- No doses, quantities or instructions presented as fact (historical recipes); describe what the book says a preparation is for in general terms.
- No content beyond what the checked lexicon says.

**Settings:**
- All entries: keyword strategy. Recursion (Geber's measured lesson: open recursion fired 55 of 97 entries on a typical line): only ungated core entries can be reached by recursion and only core content is scanned; every other entry is non-recursable and prevents further recursion; a gated entry's distinctive keys fire alone; the context list holds the book's distinctive words. These fields and the open keys are set in the first build, and the trigger test runs before any content is written.
- `order` in three tiers set by script: core subjects highest, then secondary, then the rest; budget cuts the lowest tier first.

## 4. Process
1. Lexicon written and checked first (research granularity, with references).
2. **Selection and merge list + keys** (`scripts/lorebook_rules.json`): proposed by one agent (Opus, high) from a script-built index of the lexicon (headword, kind, reference counts, whether it has its own heading, whether a paired page cites it), never the lexicon text, applied by script, **settled by a Fable reviewer before content is written** (owner, 2026-11-20: the reviewer decides, not the owner).
3. **Content:** one agent per batch (Opus, high) writes clean content from that batch's lexicon entries only; a checker (Opus, medium) checks against the lexicon: no new facts, no meta-language, no references, no doses.
4. Script builds the JSON (SillyTavern format: `entries{uid,key,keysecondary,comment,content,…}`) and fails on: empty keys, the same key on two entries, a key containing a comma, a missing plural form, content outside the length bounds, any reference pattern of this project's section ids in content, meta-labels.
5. **Trigger test** (`fire` script, which also simulates the token budget and Order): 30–50 natural chat lines about the book's subjects plus 10 everyday lines, **written by a separate agent that sees only the list of subject names, never the keys**. Acceptance: each core subject fires on its natural mentions; everyday lines fire nothing ungated; a typical line fires a handful of entries, not dozens; nothing important is cut by the budget at a typical setting. Report goes to the reviewer with the build; the owner gets a one-line result at hand-over.
