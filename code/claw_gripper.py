"""claw_gripper.py -- a claw that closes on the object.  Port E.

    import claw_gripper as claw       # give it a name, don't star-import

    claw.home()          # shut on nothing = zero, then open ready
    claw.grab()          # close and keep squeezing -> True if we caught it
    claw.release()       # open all the way again
    claw.holding()       # are we still holding it?  ask again at the far end

STALL TO FIND ZERO. TORQUE TO HOLD A THING.

ZERO IS WHERE THE JAWS MEET. home() shuts them on nothing and calls that 0,
so "did I catch something?" is just "did the jaws stop before 0?".

    0 ........... contact ........... READY_ANGLE
    jaws met      object grips        open, ready
    caught air    VARIES BY SIZE

POSITIVE OPENS -- the same way round as lift_gripper.py.

Why any of this: docs/library-design-notes.md #3.
"""

from pybricks.parameters import Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.tools import StopWatch, wait


# ============================================================ CLAW FACTS ==

CLAW_PORT = Port.E
CLAW_DIRECTION = Direction.COUNTERCLOCKWISE   # POSITIVE must mean OPENING TUNE

OPEN_SPEED = 300        # deg/s
CLOSE_SPEED = 200       # deg/s -- slower so it doesn't slam the object

HOME_EFFORT = 40        # % power, home() only. Jaw on jaw -- keep it gentle TUNE
GRIP_TORQUE = 180       # mNm -- how hard we squeeze                        TUNE

READY_ANGLE = 140       # deg open -- wide enough for your BIGGEST object   TUNE

GRIP_OVERSHOOT = 10     # deg past shut. Unreachable on purpose: the jaws never
GRIP_TARGET = -GRIP_OVERSHOOT       # arrive, so they never stop leaning in.

AIR_MARGIN = 20         # deg. Stopped below this = we caught nothing. Must be
                        # under what your SMALLEST object holds open.       TUNE
GRIP_LOAD_MIN = 60      # mNm -- below this it's resting, not squeezing     TUNE
SETTLE_MS = 150         # ms -- let the squeeze finish                      TUNE
GRIP_TIMEOUT_MS = 1500  # ms -- jammed, give up                             TUNE

LET_GO_TRAVEL = 25      # deg to open, from wherever the jaws stopped       TUNE

TIP_REACH_MM = 172      # mm from the robot's turning centre to the jaws    TUNE


# ============================================================== HARDWARE ==

claw = Motor(CLAW_PORT, CLAW_DIRECTION)
claw.control.limits(torque=GRIP_TORQUE)


# ================================================================= VERBS ==

def home():
    """Shut the jaws on NOTHING, call that zero, then open ready. Every run."""
    claw.run_until_stalled(-CLOSE_SPEED, then=Stop.COAST,
                           duty_limit=HOME_EFFORT)
    wait(200)
    claw.reset_angle(0)
    claw.run_target(OPEN_SPEED, READY_ANGLE, then=Stop.COAST)


def close_and_watch(speed, timeout_ms):
    """Close until the claw stalls, finishes, or runs out of time."""
    claw.run_target(speed, GRIP_TARGET, then=Stop.HOLD, wait=False)

    timer = StopWatch()
    wait(100)
    while timer.time() < timeout_ms:
        if claw.stalled() or claw.done():
            break
        wait(10)

    wait(SETTLE_MS)


def grab():
    """Close on the object and keep squeezing. True if we caught something."""
    close_and_watch(CLOSE_SPEED, GRIP_TIMEOUT_MS)
    # Don't stop or hold the motor here -- leaving it running is the squeeze.
    return holding()


def release():
    """Open the claw all the way and let go."""
    claw.run_target(OPEN_SPEED, READY_ANGLE, then=Stop.COAST)


def let_go(angle=None):
    """Open just far enough for the object to leave, and stop there.

    Returns the angle it opened to, so you can come back to the same width.
    """
    if angle is None:
        angle = claw.angle() + LET_GO_TRAVEL
    claw.run_target(OPEN_SPEED, angle, then=Stop.HOLD)
    return angle


# =============================================================== CHECKING ==

def grip_load(samples=5):
    """Average squeeze in mNm. abs() -- how hard, never which way."""
    total = 0
    for i in range(samples):
        total += abs(claw.load())
        wait(20)
    return total // samples


def holding():
    """Are we holding something right now?

    The jaws must have stopped short of meeting AND still be pushing.
    Ask it twice -- once at grab(), once at the far end of the mat.
    """
    if claw.angle() < AIR_MARGIN:
        return False                    # jaws met -- nothing between them
    return grip_load() > GRIP_LOAD_MIN


def show_angle():
    """Print one claw angle and load reading."""
    print("claw angle:", claw.angle(), " load:", claw.load())


# ================================ STRETCH -- the anchor run needs none of it ==
#
# Telling the notes apart is D24 and the continuation season. Everything the
# ~135-point anchor run asks of the claw is above this line.

PROBE_TORQUE = 40       # mNm -- gentle, so feel() doesn't push the note     TUNE
PROBE_SPEED = 100       # deg/s
PROBE_TIMEOUT_MS = 1200 # ms

NOTE_SMALL_MM = 30      # black, blue, white, yellow, and the microphone
NOTE_BIG_MM = 70        # green and red
BIG_ANGLE_MIN = 60      # deg. A BIG note holds the jaws further open, so it
                        # reads a BIGGER angle. Measure both with object_test TUNE


def feel():
    """Touch the object without gripping it. True if something is there.

    Same move as grab(), but too gentle to push a loose note around.
    """
    claw.control.limits(torque=PROBE_TORQUE)
    try:
        close_and_watch(PROBE_SPEED, PROBE_TIMEOUT_MS)
        return claw.angle() > AIR_MARGIN
    finally:
        claw.control.limits(torque=GRIP_TORQUE)     # always put it back


def object_size():
    """Which note is this -- 30 mm or 70 mm? None if the jaws are empty."""
    if claw.angle() < AIR_MARGIN:
        return None
    if claw.angle() >= BIG_ANGLE_MIN:
        return NOTE_BIG_MM
    return NOTE_SMALL_MM
