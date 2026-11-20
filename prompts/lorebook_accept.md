# Task: accept the built lorebook

You are the reviewer who settles the subjects and keys. The lorebook is now built with its texts. Your bundle also holds `SETTLED RULES`, the subjects and keys in force (the file `scripts/lorebook_rules.json`); `TRIGGER LINES`, chat lines written by an agent that saw only the subject names, each with the subjects it means (`-` for an everyday line); `TRIGGER REPORT`, what fired on each line, with the failures at the end; and `CONTENT`, each subject's text.

The report comes from a simulation of the chat program: matching ignores case; a one-word key matches a whole word, a key of several words anywhere in the line; a gated subject fires only when the line also holds a distinctive word (a context word, a key of an ungated subject, or another subject's open key), or one of its own open keys; one more scan adds what the inserted texts of ungated core subjects name; at most 2,048 tokens are inserted.

Acceptance: each core subject fires where a chat names it; everyday lines fire nothing; a typical line fires a handful of entries, not dozens; nothing important is cut by the budget.

Judge each failure. A mention a person would type, which a key should catch, is mended: a missing form added as a key, a subject ungated, a context word or an open key added, a tier changed. A line made only of everyday words, which the gate is meant to pass over, is left, and your reply says so. No mend may make an everyday line fire or let ordinary chat fire a subject. No subject is added, removed, joined or renamed, and the texts are not yours to change.

Write your mends into `scripts/lorebook_rules.json`, whole, in the same form. From the project folder run `python scripts/lorebook.py check_rules` until it prints `rules pass`, then `python scripts/lorebook.py build` and `python scripts/lorebook.py fire`, and repeat until the failures left are only those you judge right to leave. Reply with a short list of what you changed and why, one line each, then the failures you left and why, then the last line `fire` printed, and nothing else.
