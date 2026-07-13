# Slide decks — day → deck map

One reveal.js deck per curriculum day, named by **topic** (not day number), so reordering the
curriculum never breaks file paths or rendered URLs.

> **Convention:** day numbers live only in each deck's front-matter `subtitle` and in this table —
> **never** in filenames or slide prose. Inside decks, refer to other sessions by topic
> ("next: *Drive a Square*"), not by day number. When the schedule changes, update this table and
> the affected subtitles; nothing else moves. (Proven by decision #20: the `DriveBase` reveal moved
> D5 → D10 and `drivebase-shortcut.qmd` kept its name and URL.)

Curriculum source: `docs/Robot_Rockstars_Bootcamp_Plan.md` — the week-by-week day table and the
D1–D25 authoring map.

Kid-facing landing page: root `index.qmd` → `output/index.html` — a colorful card grid of all 25
sessions (D1–D7, D9, D10 link to their decks; the rest show "Coming soon"). Update its cards when
a planned deck goes live.

## Week 1 — Build, Drive, Sense

| Day | Deck | Topic |
|:--:|---|---|
| D1 | [build-and-test.qmd](build-and-test.qmd) | Welcome + WRO orientation, bench tour, build a great base (2–3 h), power-on gate |
| D2 | [make-it-move.qmd](make-it-move.qmd) | Human-robot game, first program + variables, speed = distance ÷ time, deg/s → cm/s wheel math, `run_time` vs `run_angle`, *Radar Gun* |
| D3 | [drive-a-square.qmd](drive-a-square.qmd) | Break-it square (turns drift), `for`/`while` + colon/indent bug hunts, feel the gyro, watched turn → momentum quiz, loop shapes (360 ÷ n), *Shape Shifter* |
| D4 | [pid-on-the-gyro.qmd](pid-on-the-gyro.qmd) | Coast cured (arrive slowly) → two-speed `gyro_turn` + first `def` (+ "silent robot" bug hunt), P-term felt then named: `speed = error × gain` turn + self-healing straight, gain tuning, *Nudge Wars* |
| D5 | [name-your-moves.qmd](name-your-moves.qmd) | D + I complete PID (I = coach demo only), then the library begins: `my_lib.py` with `turn_to` · `drive_straight` · `drive_square`, *Bullseye* on their own `drive_straight` |

## Week 2 — Program the Robot, Build the Library, Form the Teams

| Day | Deck | Topic |
|:--:|---|---|
| D6 | [stop-patrol-react.qmd](stop-patrol-react.qmd) | Motor-as-sensor (`run_until_stalled` + measured back-off), `if/else`, patrol loop, `drive_to_wall` + `wall_square` into `my_lib.py`, anchor-first scoring map |
| D7 | [pd-line-following.qmd](pd-line-following.qmd) | Bang-bang → P line-following + junction squaring (the gate); `kd` upgrade as stretch; `follow_line` + `square_on_line` into `my_lib.py` |
| D8 | `library-gauntlet.qmd` *(planned)* | Library consolidation into one module (Good Practices) + multi-station challenge gauntlet |
| D9 | [mission-list.qmd](mission-list.qmd) | Lists (index/iterate/append), steps as functions, the blocking mission runner, *Setlist* |
| D10 | [drivebase-shortcut.qmd](drivebase-shortcut.qmd) | Draft Day: `RobotConfig` (the merge break-it), the earned `DriveBase` reveal, team split + robot selection, *Mini Mission* finale |

## Week 3 — Build the Mechanisms, Chain the Anchor Run

| Day | Deck | Topic |
|:--:|---|---|
| D11 | `cables-and-microphone.qmd` *(planned)* | Team mechanism build #1: cables (30) + microphone (20) |
| D12 | `instruments-and-avoidance.qmd` *(planned)* | Team mechanism build #2: instruments (45) + bonus-by-avoidance (+40) |
| D13–D14 | *(planned — day split set at the Draft-Day planning pass)* | Segments integrated into the mission runner |
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
