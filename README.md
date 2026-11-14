# The Editor's Corkboard — Friday 13 November 2026

A make.fun news-image-01 entry. The program draws one 1024x1024 PNG:
an editor's corkboard in a wood frame, with six news clippings pinned
to it, each with a small pictogram, a bold headline and a one-paragraph
summary. Every story happened or was first reported on Friday
13 November 2026.

## The six stories

1. **Senate summons Huang** — the US Senate Banking panel calls Nvidia
   chief Jensen Huang and the Commerce secretary to testify on chip exports.
2. **Drone hits Russian warship** — Kyiv says a drone struck a Russian
   warship in the Gulf of Finland.
3. **FBI: $400M FaceStealer hack** — North Korean hackers used fake video
   calls to steal $400M in crypto, the FBI says.
4. **Microsoft outage, day two** — the global Microsoft 365 outage
   disrupts Outlook, Teams and courts for a second day.
5. **Qatar–Turkey defence pact** — Doha and Ankara sign a mutual defence
   deal in Istanbul.
6. **Kane breaks caps record** — Harry Kane wins a record 126th England
   cap as England beat Croatia 2-1 at Wembley.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Pure Python 3 standard library, no network. The PNG is encoded by hand
(zlib) and all text is set in a 5x7 bitmap font defined in `main.py`.
Deterministic: two runs write byte-identical files.
