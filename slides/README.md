# Slide decks — day → deck map

One reveal.js deck per curriculum day, named by **topic** (not day number), so reordering the
curriculum never breaks file paths or rendered URLs.

> **Convention:** day numbers live only in each deck's front-matter `subtitle` and in this table —
> **never** in filenames or slide prose. Inside decks, refer to other sessions by topic
> ("next: *Drive a Square*"), not by day number. When the schedule changes, update this table and
> the affected subtitles; nothing else moves.

Curriculum source: `docs/Robot_Rockstars_Bootcamp_Plan.md` — the week-by-week day table and the
D1–D25 authoring map.

Kid-facing landing page: root `index.qmd` → `output/index.html` — a colorful card grid of all 25
sessions (D1–D5 link to their decks; D6–D25 show "Coming soon"). Update its cards when a planned
deck goes live.

## Week 1 — Build, Drive, Sense

| Day | Deck | Topic |
|:--:|---|---|
| D1 | [build-and-test.qmd](build-and-test.qmd) | Welcome + WRO orientation, bench tour, build a great base (2–3 h), power-on gate |
| D2 | [make-it-move.qmd](make-it-move.qmd) | Human-robot game, first program + variables, speed = distance ÷ time, deg/s → cm/s wheel math, `run_time` vs `run_angle`, *Radar Gun* |
| D3 | [drive-a-square.qmd](drive-a-square.qmd) | Break-it square (turns drift), `for`/`while` + colon/indent bug hunts, feel the gyro, watched turn → momentum quiz, loop shapes (360 ÷ n), *Shape Shifter* |
| D4 | [pid-on-the-gyro.qmd](pid-on-the-gyro.qmd) | Coast cured (arrive slowly) → two-speed `gyro_turn` + first `def` (+ "silent robot" bug hunt), P-term felt then named: `speed = error × gain` turn + self-healing straight, gain tuning, *Nudge Wars* |
| D5 | [drivebase-shortcut.qmd](drivebase-shortcut.qmd) | D + I complete PID (I = demo only), wheel/track geometry, `DriveBase` as the earned shortcut, *Bullseye* |

## Week 2 — Score the Field, Form the Teams

| Day | Deck | Topic |
|:--:|---|---|
| D6 | `stop-patrol-react.qmd` *(planned)* | Motor-as-sensor, stall + back-off, `if/else`, patrol loop, `DriveBase` precision pass, scoring map |
| D7 | `pd-line-following.qmd` *(planned)* | Bang-bang → P → PD on the line in one day + junction squaring (I-term as stretch) |
| D8 | `cables-and-microphone.qmd` *(planned)* | Mechanism #1: cables (30) + microphone (20) |
| D9 | `instruments-and-avoidance.qmd` *(planned)* | Mechanism #2: instruments (45) + bonus-by-avoidance (+40) |
| D10 | `gold-reference-and-teams.qmd` *(planned)* | Gold-reference gate, team split, `RobotConfig` |

## Week 3 — Chain the Anchor Run

| Day | Deck | Topic |
|:--:|---|---|
| D11 | `mission-list.qmd` *(planned)* | Lists + the blocking mission runner |
| D12 | `integrate-cables.qmd` *(planned)* | Cables segment inside the run |
| D13 | `integrate-instruments.qmd` *(planned)* | Instruments segment inside the run |
| D14 | `integrate-mic-avoidance.qmd` *(planned)* | Microphone + avoidance inside the run |
| D15 | `assemble-anchor-run.qmd` *(planned)* | Full ~135 anchor chained end-to-end |

## Week 4 — Make It Reliable

| Day | Deck | Topic |
|:--:|---|---|
| D16 | `lock-the-anchor.qmd` *(planned)* | Anchor ≤ 2:00, ×10 clean |
| D17 | `reliability-root-cause.qmd` *(planned)* | Failure logging, root-cause, calibration log |
| D18 | `fixed-notes-tech-summary.qmd` *(planned)* | Fixed notes (+40 → ~175), Technical Summary draft |
| D19 | `robustness-hsv.qmd` *(planned)* | HSV calibration, retry logic, venue hardening |
| D20 | `reliability-checkpoint.qmd` *(planned)* | Week-4 gate: ~175 ×20 ≥ 90% |

## Week 5 — Color, Notes & the Mock Qualifier

| Day | Deck | Topic |
|:--:|---|---|
| D21 | `randomized-notes.qmd` *(planned)* | Color → target map, randomized notes (+80 stretch) |
| D22 | `tech-summary-drill.qmd` *(planned)* | Summary finalized, both members interview-ready |
| D23 | `mock-qualifier.qmd` *(planned)* | Check-time sim, Surprise Rule, head-to-head |
| D24 | `full-255-push.qmd` *(planned)* | Full-255 chase + lock the strongest config |
| D25 | `selection-handoff.qmd` *(planned)* | Selection, continuation plan, showcase |
