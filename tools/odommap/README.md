# OdomMap (vendored) — field measuring tool

Vendored from [haing2811/OdomMap](https://github.com/haing2811/OdomMap) (MIT
License — see `LICENSE`; © the upstream author). Only the files this bootcamp
needs are included: the single-page app, its logos, and the **WRO 2026
RoboMission Elementary** field image (verified against
`docs/WRO-2026-RoboMission-Elementary-Game-Rules.pdf` — it is the official
*Robot Rockstars* mat). Other years/categories were dropped; selecting them in
the app will show a missing image.

## Usage

Coach tooling for route planning. The odometry-mode origin bar is the concrete
picture of `reset_heading(0)`, which makes it a useful thing to put on a screen
when a squad is arguing about where zero is.

1. Open `OdomMap.html` in a browser (works fully offline).
2. Pick **2026 / Elementary**, set **Wheel (mm) = 88** (the gold reference's
   wheel — `WHEEL_DIAMETER` in the `ROBOT FACTS` block of `code/movements.py`).
   Field is 2362 × 1143 mm.
3. **Normal mode** — click two points: distance in mm, wheel rotations/degrees
   (seed values for `drive_straight()` calls; final numbers are still tuned on
   the physical mat).
4. **Odometry mode** — set an origin (e.g. the start-area corner) and read
   object coordinates: paste these over the `# ESTIMATE` values in
   `../route_optimizer/field_data.py`.
5. **Route mode** — click out a multi-leg detour (e.g. around the clef or the
   stage speakers) and use its total length as an `ARC_OVERRIDES` entry in
   `field_data.py` to un-forbid a leg the optimizer blocked.

Used on **D18** (mission planning — the path plan with marked reset points) and
again when segments are ordered for time and the randomized-note branch is
prepped — see `../route_optimizer/` and the plan's day table for current days.

> ⚠️ **Two frames on one mat — they are 90° apart.** This tool's odometry mode
> measures headings **clockwise from "up"** (`atan2(dx, -dy)`; 0 = up, 90 =
> right, 180 = down, −90 = left), which matches Pybricks `hub.imu.heading()`
> and therefore `turn_to()`. But `../route_optimizer/field_data.py` measures
> **from +X toward +Y** (0 = right, 90 = down) because it works in image
> coordinates. Convert with **`map_heading = field_heading + 90`**. Concretely,
> `CABLE_HEADING_DEG` of `100.0` / `80.0` (field) is **190° / 170°** to the
> robot. Pasting the raw field number into `turn_to()` lays the cable sideways
> and silently costs 15 anchor points — the cable is 128 mm and the grey area's
> short axis is only 79.7 mm.
