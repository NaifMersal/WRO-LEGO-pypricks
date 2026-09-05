"""claw_gripper.py -- a claw that closes on the object.  Port E.

    import claw_gripper as claw       # give it a name, don't star-import

    claw.home()          # open all the way, call that zero
    claw.grab()          # close and keep squeezing -> True if we caught it
    claw.release()       # open all the way again
    claw.holding()       # are we still holding it?  ask again at the far end

    claw.let_go()        # open just enough to free the object
    claw.feel()          # touch without gripping -> True if something's there
    claw.object_size()   # 30 or 70 mm -- which note is this?
"""

from pybricks.parameters import Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.tools import StopWatch, wait


# ============================================================ CLAW FACTS ==

CLAW_PORT = Port.E
CLAW_DIRECTION = Direction.CLOCKWISE   # positive must mean CLOSING

OPEN_SPEED = 300        # deg/s
CLOSE_SPEED = 200       # deg/s -- slower so it doesn't slam the object

HOME_EFFORT = 75        # % power, home() only                            TUNE
GRIP_TORQUE = 180       # mNm -- how hard we squeeze                      TUNE
EMPTY_ANGLE = 144       # deg, empty jaws shut. Measure with object_test  TUNE
GRIP_OVERSHOOT = 4      # deg past the jaws, so the claw never stops leaning
GRIP_ANGLE = EMPTY_ANGLE + GRIP_OVERSHOOT       # DERIVED -- never type this

AIR_MARGIN = 5          # deg of slack before we call it air              TUNE
GRIP_LOAD_MIN = 60      # mNm -- below this it's resting, not squeezing   TUNE
SETTLE_MS = 150         # ms -- let the squeeze finish                    TUNE
GRIP_TIMEOUT_MS = 1500  # ms -- jammed, give up                           TUNE

LET_GO_TRAVEL = 25      # deg to open, from wherever the jaws stopped     TUNE

TIP_REACH_MM = 172      # mm from the robot's turning centre to the jaws  TUNE

NOTE_SMALL_MM = 30      # black, blue, white, yellow, and the microphone
NOTE_BIG_MM = 70        # green and red
BIG_ANGLE_MAX = 130     # deg. A WIDE note stops the jaws EARLY, so a big
                        # note reads a SMALL angle.                       TUNE

PROBE_TORQUE = 40       # mNm -- gentle, so feel() doesn't push the note  TUNE
PROBE_SPEED = 100       # deg/s
PROBE_TIMEOUT_MS = 1200 # ms


# ============================================================== HARDWARE ==

claw = Motor(CLAW_PORT, CLAW_DIRECTION)
claw.control.limits(torque=GRIP_TORQUE)


# ================================================================= VERBS ==

def home():
    """Open all the way into the end stop and call that zero."""
    claw.run_until_stalled(-OPEN_SPEED, then=Stop.COAST,
                           duty_limit=HOME_EFFORT)
    wait(200)
    claw.reset_angle(0)


def close_and_watch(speed, timeout_ms):
    """Close until the claw stalls, finishes, or runs out of time."""
    claw.run_target(speed, GRIP_ANGLE, then=Stop.HOLD, wait=False)

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
    claw.run_target(OPEN_SPEED, 0, then=Stop.COAST)


def let_go(angle=None):
    """Open just far enough for the object to leave, and stop there.

    Returns the angle it opened to, so you can come back to the same width.
    """
    if angle is None:
        angle = claw.angle() - LET_GO_TRAVEL
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

    The jaws must have stopped short AND still be pushing.
    """
    if claw.angle() > EMPTY_ANGLE - AIR_MARGIN:
        return False                    # jaws met -- nothing between them
    return grip_load() > GRIP_LOAD_MIN


def feel():
    """Touch the object without gripping it. True if something is there.

    Same move as grab(), but too gentle to push a loose note around.
    """
    claw.control.limits(torque=PROBE_TORQUE)
    try:
        close_and_watch(PROBE_SPEED, PROBE_TIMEOUT_MS)
        return claw.angle() < EMPTY_ANGLE - AIR_MARGIN
    finally:
        claw.control.limits(torque=GRIP_TORQUE)     # always put it back


def object_size():
    """Which note is this -- 30 mm or 70 mm? None if the jaws are empty."""
    if claw.angle() > EMPTY_ANGLE - AIR_MARGIN:
        return None
    if claw.angle() <= BIG_ANGLE_MAX:
        return NOTE_BIG_MM
    return NOTE_SMALL_MM


def show_angle():
    """Print one claw angle and load reading."""
    print("claw angle:", claw.angle(), " load:", claw.load())
