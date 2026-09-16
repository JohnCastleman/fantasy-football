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
   (weekly-only optional mid-week updates). The FP/Flock runs in sync with Ron's
   publishings are the canonical runs of these scripts; other optional runs can occur
   before — as the live data becomes available — or after, for freshness.
4. **Backups are manual, in-sheet, no automation.** See Backup discipline below.

## Ron's publish schedule (CT)

Source: Ron's content-schedule post (ET → CT):

- **Tue by 4:30pm CT** — Waiver/FAAB Report article
- **Wed by 8:00am CT** — Rest-of-Season rankings (as of Week w)
- **Thu by 3:00pm CT** — Weekly rankings (before TNF)
- **Sun 10:00am CT** — Weekly rankings update (+ 10–11am CT Start/Sit stream, watch-only)

Waivers process Wed ~midnight (Tue night late), so the Tue waiver write has a hard
evening deadline.

## Backup discipline (manual)

- **Waiver tabs:** no backup. Tab title is unique per week (`Wn waivers`), written 1×/week.
- **Ron ROS + Weekly tabs:** before the first W(n+1) overwrite, duplicate the current tab
  to `"<base name>(Wn)"`. Keep one backup generation only: when creating `(Wn)`
  backups, delete the `(Wn-1)` backups. Backup is created once per week even though
  Weekly is usually written multiple times (ROS is rarely written more than once).

## Tue — Waiver day (deadline: before Wed ~midnight waiver run)

Ron waiver Doc (usually Tue midday+, SLA 4:30pm CT) — scripted (GDoc format is
Sheets-hostile):

```powershell
python tools/waiver-report/ron-stewart-weekly-waiver-report-to-json.py <doc_id_or_url> --html
# → docs/waiver-reports/W<n> waivers.json (+ .html)

python tools/waiver-report/waiver-report-json-to-google-sheets-tab.py "docs/waiver-reports/W<n> waivers.json"
# → tab "W<n> waivers" (temp-tab-then-rename)
```

Optional early full refresh (live sources are already fresh Tue; overwrite same files).
These are optional pre-runs; the canonical runs follow Ron's Wed/Thu publishings below.
See Appendix for the FP and Flock command patterns.

## Wed — ROS day (from 8:00am CT)

1. **Manual:** rotate backup (delete `(Wn-1)` ROS backup, duplicate current ROS tab →
   `"<name>(Wn)"`), then copypasta Ron's ROS-as-of-Wn grid.
2. **FP ROS overlay — canonical ROS run** (targets: `FantasyPros ROS K/DST rankings`
   L3 = K, Q3 = DST; 4 cols `rank, name, team, bye`): FP ROS commands from Appendix.
   Verify team/BYE lookups feeding the roster table.
3. **Flock ROS overlay — canonical ROS run** (target: `Flock ROS raw data`, col L row 3):
   Flock ROS paste → TSV (`docs/flock-rankings/flock-ROS(W<n>).tsv`) → Sheets command
   from Appendix.

ROS is rarely re-run after Wed.

## Thu — Weekly day (before TNF; Ron SLA 3:00pm CT)

1. **Manual:** rotate backup for the Weekly tab (same one-generation rule), copypasta
   Ron's Weekly grid. Expect possible mid-week updates — backup is still created once.
2. **FP Weekly overlay — canonical Weekly run** (targets: `FantasyPros weekly K/DST rankings`
   N3 = K, S3 = DST; 4 cols `rank, name, team, opponent`; DST `--week` also stamps I1):
   FP Weekly commands with `--week <N>` from Appendix.
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
