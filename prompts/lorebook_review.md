# Task: settle the lorebook's subjects and keys

You are the reviewer. Your bundle also holds `PROPOSAL`, another agent's subjects and keys written to the task above; `SCRIPT FINDINGS`, what the rule check found in it; and `JOINED ENTRIES`, the word-list entries of every headword the proposal joins with another. Your decision is final: write the settled object yourself.

Check, and mend what fails:
- Every join: the joined entries show the book itself takes them as one thing (one spelling, form or name of the other, or the text saying they are the same). A join they do not bear out is split, or the weaker headword left out.
- The selection: every central headword is a subject, inside a subject, or left out for one of the reasons above; nothing that is not central stands as a subject of its own. The threshold is set by the script; where it lets in subjects no chat would name or keeps out ones it would, say so in your reply and change the selection, each change with its reason.
- The keys: what a person would type today, every form, nothing that ordinary chat would hold unless the subject is gated, no key on two subjects. Each script finding is mended.
- The tiers and the gating: the core is what a chat about the book turns on; every everyday-word key is gated; the context words mark this book's subjects and nothing else.

Write the settled object, whole, in the same form, to the file your task names; run `python scripts/lorebook.py check_rules <your file>` from the project folder and correct until it prints `rules pass`. Reply with a short list of what you changed and why, one line each, and nothing else.
