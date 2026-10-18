# Weekly Runbook — NFL In-Season (Tue-earliest)

This is the day-to-day operating loop for the fantasy tracker sheet during the NFL season.
It is a design goal that the scripts remain immutable throughout the season; weekly runs
are data-only (local snapshot → Sheets write). Occasionally — especially the waiver
report's GDoc format — the source format drifts and the associated script needs
tinkering to keep working; that is the exception, not the rule.
`*-sheets.json` configs are gitignored and change once at season start (the same
multi-tab sheet is used all season; a new sheet is copied/started at the next season).
The Google API token (`%APPDATA%/fantasy-football-tools/token.pickle`, Windows) is
intended to be refreshed once at season start, and again as needed due to staleness.

> **Note (deferred): Flock / Mason Dodd runs are documented inline below alongside the
> FP runs, exactly as previously run. Flock runs are deferred for now, and the Flock
> tool scripts will likely need TLC to adapt to his streamlined 2026 formats before
> they work again.**

## Principles

1. **Nothing runs before Tue.** MNF ends ~midnight ET Mon plus source lag — Tue is the
   earliest sensible run day for anything.
2. **Local intermediaries are snapshots, not cache.** Every run is
   `fetch → local file (overwrite same path) → Sheets write` in one go. Never
   write-then-wait, never re-write the same file twice without regenerating.
   - `docs/kdst-rankings/kdst-ROS(Wn)-K.tsv`, `kdst-ROS(Wn)-DST.tsv`, `kdst-Wn-K.tsv`, `kdst-Wn-DST.tsv`
   - `docs/flock-rankings/flock-ROS(Wn).tsv`, `flock-Wn-QB|RB|WR|TE.tsv` (+ `.html` previews)
   - `docs/waiver-reports/Wn waivers.json` (+ `.html`)
3. **Ron is the anchor; FP + Flock layer on top.** Ron publishes 1×/week per slot
   plus an optional Wed "First Look" weekly (non-canonical preview).
   The Tue FP runs are the canonical runs
   of those scripts (live FP data is already fresh Tue); Flock ROS may also run
   canonical Tue (ahead of Ron's Wed ROS). Later same-week runs in sync with Ron's
   Wed/Thu publishings — or after, for freshness — are "refresh" runs (same
   overwrite + rewrite pattern). Flock Weekly stays synced with Ron's Thu Weekly
   for now; its scripts still need TLC for the streamlined 2026 formats.
4. **Backups are manual, in-sheet, no automation.** See Backup discipline below.

## Ron's publish schedule (CT)

Source: Ron's content-schedule post (ET → CT):

- **Tue by 4:30pm CT** — Waiver/FAAB Report article
- **Wed by 8:00am CT** — Rest-of-Season rankings (as of Week w)
- **Wed ~4:00pm CT** — Weekly rankings "First Look" (non-canonical: no tiers,
  no flex table; whether this continues is TBD — first observed W6 2026)
- **Thu by 3:00pm CT** — Weekly rankings, canonical (before TNF)
- **Sun 10:00am CT** — Weekly rankings update (+ 10–11am CT Start/Sit stream, watch-only)

Waivers process Wed ~midnight (Tue night late). That is the league's waiver
deadline and therefore Ron's publish deadline for at least the waiver report
(sometimes ROS too) — not a deadline for our scripted runs, which may slip
to Wed morning when convenient.

## Backup discipline (manual)

- **Waiver tabs:** no backup. Tab title is unique per week (`Wn waivers`), written 1×/week.
- **Ron ROS + Weekly tabs:** before the first W(n+1) overwrite, duplicate the current tab
  to `"<base name>(Wn)"`. Keep one backup generation only: when creating `(Wn)`
  backups, delete the `(Wn-1)` backups. Backup is created once per week, ahead of
  the week's FIRST Weekly overwrite — normally Wed before the First Look paste;
  if Wed is skipped, take it Thu before the canonical paste instead. All later
  re-pastes (Thu/Sun) overwrite the live tab with no further backup
  (ROS is rarely written more than once).

## Tue — Waiver day (no hard deadline for our runs; may slip to Wed morning)

Ron waiver Doc (usually Tue midday+, SLA 4:30pm CT) — scripted (GDoc format is
Sheets-hostile):

```powershell
python tools/waiver-report/ron-stewart-weekly-waiver-report-to-json.py <doc_id_or_url> --html
# → docs/waiver-reports/W<n> waivers.json (+ .html)

python tools/waiver-report/waiver-report-json-to-google-sheets-tab.py "docs/waiver-reports/W<n> waivers.json"
# → tab "W<n> waivers" (temp-tab-then-rename)
```

Optional early Flock ROS run (usually ready Tue; overwrite same files).
Flock Weekly stays synced with Ron's Thu Weekly for now. See Appendix for the
Flock command patterns.

FP canonical runs (live FP data is already fresh Tue; overwrite same files):

```powershell
node -e "import('./client/dump.js').then(m => m.dumpRosKRankings({outputFile: 'docs/kdst-rankings/kdst-ROS(W<n>)-K.tsv'}))"
python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --input "docs/kdst-rankings/kdst-ROS(W<n>)-K.tsv" --position K --type ROS
# DST: same, position DST → Q3.

node -e "import('./client/dump.js').then(m => m.dumpWeeklyKRankings({outputFile: 'docs/kdst-rankings/kdst-W<n>-K.tsv'}))"
python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --input "docs/kdst-rankings/kdst-W<n>-K.tsv" --position K --type WEEKLY --week <N>
# DST: same, position DST → S3 (also stamps I1).
```

Targets: FP ROS K `L3` / DST `Q3` on `FantasyPros ROS K/DST rankings`;
FP Weekly K `N3` / DST `S3` on `FantasyPros weekly K/DST rankings`.
Possible later "refresh" runs alongside Ron's Wed/Thu publishings reuse the same
files and ranges.

## Wed — ROS day (from 8:00am CT) + Weekly "First Look" (from ~4:00pm CT)

> **W6 2026 playtest:** First Look pastes into the Weekly tab the same way as
> the canonical Thu grid. It must NOT touch the ROS tab — ROS has no flex
> table in First Look, and the ROS-grid name lookups feeding pos/tm on the
> GeekSquadron tab would break. Limited value is still derivable on the
> GeekSquadron pivot-ish table by ignoring overall-rk and pos-tier cols and
> sorting on pos-rk alone.

1. **Manual:** rotate backup (delete `(Wn-1)` ROS backup, duplicate current ROS tab →
   `"<name>(Wn)"`), then copypasta Ron's ROS-as-of-Wn grid.
2. **FP ROS overlay — "refresh" run if needed** (targets: `FantasyPros ROS K/DST rankings`
   L3 = K, Q3 = DST; 4 cols `rank, name, team, bye`): FP ROS commands from Appendix
   (same files, same ranges as the Tue canonical run).
   Verify team/BYE lookups feeding the roster table.
3. **Flock ROS overlay — canonical ROS run** (target: `Flock ROS raw data`, col L row 3):
   Flock ROS paste → TSV (`docs/flock-rankings/flock-ROS(W<n>).tsv`) → Sheets command
   from Appendix.

ROS is rarely re-run after Wed (FP ROS "refresh" only if needed; Flock ROS stays
canonical Tue unless its scripts get fixed for a later slot).

4. **Manual — Weekly "First Look" (non-canonical):** rotate Weekly backup first
   (delete `(Wn-1)` Weekly backup, duplicate current Weekly tab → `"<name>(Wn)"`),
   then copypasta Ron's First Look weekly grid into the live Weekly tab.
   Later re-pastes (Thu canonical, Sun update) overwrite this same live tab with
   no further backup.

## Thu — Weekly day, canonical (before TNF; Ron SLA 3:00pm CT)

1. **Manual:** copypasta Ron's canonical Weekly grid into the live Weekly tab
   (over the First Look, if pasted). No backup if Wed already took it — but if Wed
   was skipped, rotate the Weekly backup FIRST (same one-generation rule), since
   this is the week's first overwrite.
2. **FP Weekly overlay — "refresh" run if needed** (targets: `FantasyPros weekly K/DST rankings`
   N3 = K, S3 = DST; 4 cols `rank, name, team, opponent`; DST `--week` also stamps I1):
   FP Weekly commands with `--week <N>` from Appendix (same files, same ranges as
   the Tue canonical run).
3. **Flock Weekly overlay — canonical Weekly run** (target: `Flock weekly raw data`;
   QB:G3 RB:X3 WR:AN3 TE:AY3): paste each position →
   `docs/flock-rankings/flock-W<n>-<POS>.tsv` → Sheets per position (Appendix).

## Sun — Weekly update (10:00am CT)

- Ron Weekly update: manual re-paste into the Weekly tab. No new backup.
- Optional FP/Flock freshness re-run (overwrite same local files, rewrite same ranges).
- Start/Sit stream 10–11am CT: watch-only, no script.

## Fri / Sat / Mon night

No scheduled runs. Optional FP/Flock freshness re-runs only (same overwrite + rewrite
pattern). No runs before Tue per MNF lag rule.

## Appendix — command patterns, targets, season rollover, auth

FP (file-backed variant keeps the snapshot intermediary):

```powershell
node -e "import('./client/dump.js').then(m => m.dumpRosKRankings({outputFile: 'docs/kdst-rankings/kdst-ROS(W<n>)-K.tsv'}))"
python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --input "docs/kdst-rankings/kdst-ROS(W<n>)-K.tsv" --position K --type ROS
# DST: same, position DST → Q3. Weekly: dump-weekly-k/dst.js + --type WEEKLY --week <N> → N3/S3.
# Pipe variant: node tools/kdst-rankings/dump-ros-k.js 2>$null | python tools/kdst-rankings/fantasypros-kdst-rankings-to-google-sheets.py --position K --type ROS
```

Flock (paste → TSV → Sheets):

```powershell
python tools/flock-rankings/dump-ros.py --week <N> --html | python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py --type ROS
python tools/flock-rankings/dump-weekly-qb.py --week <N> --html | python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py --type WEEKLY --position QB
# ... repeat for RB, WR, TE
```

- Paste targets: FP ROS K `L3` / DST `Q3`; FP Weekly K `N3` / DST `S3`;
  Flock ROS `Flock ROS raw data L3`; Flock Weekly QB `G3`, RB `X3`, WR `AN3`, TE `AY3`.
- Season start: copy prior W17 weekly sheet → new season sheet, update each
  `*-sheets.json` once to the new ID (old sheet keeps old GID; writing to a stale ID
  hits the wrong sheet). `server/settings.js season` is a hardcoded rollover.
- Auth: `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` from the stored-
  credentials launcher; token auto-refresh is built into `get_credentials()` and only
  rewrites the pickle on refresh/re-auth, not on every valid run. Refresh once at
  season start, again as needed.
- Pre-season corner case (recorded): before the season opener, FP ROS may be stale/absent
  while Draft is fresh — verified for the 2026 preseason that ROS is fresh, so ROS is
  used from the start.
