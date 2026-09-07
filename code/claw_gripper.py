"""claw_gripper.py -- a claw that closes on the object.  Port E.

    import claw_gripper as claw       # give it a name, don't star-import

    claw.home()          # shut on nothing = zero, then open ready
    claw.grab()          # close and keep squeezing
    claw.release()       # open all the way again
    claw.release(50)     # ...or open only THIS far, so the jaws shove nothing

STALL TO FIND ZERO. TORQUE TO HOLD A THING.

ZERO IS WHERE THE JAWS MEET. home() shuts them on nothing and calls that 0,
so an angle is simply how far the object holds the jaws open.

    0 ........... contact ........... READY_ANGLE
    jaws met      object grips        open, ready
                  VARIES BY SIZE

POSITIVE OPENS -- the same way round as lift_gripper.py.

Why any of this: docs/library-design-notes.md #3.
"""

from pybricks.parameters import Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.tools import wait


# ============================================================ CLAW FACTS ==

CLAW_PORT = Port.E
CLAW_DIRECTION = Direction.COUNTERCLOCKWISE   # POSITIVE must mean OPENING TUNE

OPEN_SPEED = 300        # deg/s
CLOSE_SPEED = 200       # deg/s -- slower so it doesn't slam the object

HOME_EFFORT = 40        # % power, home() only. Jaw on jaw -- keep it gentle TUNE
GRIP_TORQUE = 180       # mNm -- how hard we squeeze                        TUNE

READY_ANGLE = 140       # deg open -- wide enough for your BIGGEST object   TUNE
GRIP_TARGET = -10       # deg past shut. Unreachable on purpose: the jaws never
                        # arrive, so they never stop leaning in.


# ============================================================== HARDWARE ==

claw = Motor(CLAW_PORT, CLAW_DIRECTION)
claw.control.limits(torque=GRIP_TORQUE)


# ================================================================= VERBS ==

def home():
    """Shut the jaws on NOTHING, call that zero, then open ready. Every run."""
    claw.run_until_stalled(-CLOSE_SPEED, then=Stop.COAST,
                           duty_limit=HOME_EFFORT)
    wait(200)                       # let it settle, or zero drifts
    claw.reset_angle(0)
    claw.run_target(OPEN_SPEED, READY_ANGLE, then=Stop.COAST)


def grab():
    """Close on the object and keep squeezing whatever stopped the jaws."""
    claw.run_target(CLOSE_SPEED, GRIP_TARGET, then=Stop.HOLD, wait=False)
    wait(100)                           # let it get moving before asking
    while not claw.stalled() and not claw.done():
        wait(10)
    # Don't stop or hold the motor here -- leaving it running IS the squeeze.


def release(angle=READY_ANGLE):
    """Open the claw and let go. A smaller angle opens less.

    Zero is where the jaws meet, so the number is just how far open you want
    them: release() swings wide, release(50) barely lets go. Use a small one
    beside something you must not knock over, like the microphone.
    """
    claw.run_target(OPEN_SPEED, angle, then=Stop.COAST)
