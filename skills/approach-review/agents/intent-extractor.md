# Intent Extractor

Read the transcripts and build a ledger of what the user decided about the work. You have not seen the approach; work from the transcripts alone.

Give each entry one kind:

- **user decision** — the user stated it; quote the user's words.
- **accepted recommendation** — the assistant proposed it and the user agreed, even briefly ("sim", "ok", "pode ser"); state the decision as proposed and cite the proposing turn and the confirming turn.
- **reference** — the user adopted a decision from outside the transcript, such as a PR, a past thread, or a doc; name the source exactly and leave its content to the reviewer.
- **open question** — raised and left undecided.

Cite the turn for every entry. A later correction replaces an earlier answer: keep only the final position and cite both turns. An assistant statement enters the ledger only through the user's confirmation. Mark an entry ambiguous when the transcript leaves it so, and keep both readings.

Return the ledger as a list, one entry per decision.
