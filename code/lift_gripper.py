"""lift_gripper.py -- jaws that GRIP an object, then LIFT it.  Port C.

    from movements import *
    import lift_gripper as lift       # named, NEVER star-imported

    lift.home()                       # shut on nothing = zero, then open ready
    lift.grab()                       # squeeze, then raise -> True if carrying
    lift.release()                    # set down and open
    lift.holding()                    # ask again at the far end

ONE MOTOR, ONE CONTINUOUS MOVE, TWO OUTCOMES. The jaws close until the object
stops them. Keep turning the same way and the jaws can't move any more -- so
the frame levers up around them instead, and the object rides up with it.

    +140 ........ contact ........ 0 ....... contact - LIFT_TRAVEL
    open, ready   object grips     jaws met  UP and carrying
                  VARIES BY SIZE   on air

PHASE 1 IS TORQUE, PHASE 2 IS ANGLE -- AND PHASE 2 COUNTS FROM CONTACT, NOT
FROM ZERO. A big base stops the jaws at +45, a small one at +20; an absolute
lift target would swing them to different heights. LIFT_TRAVEL is degrees
*past contact*, so every object rises the same amount.

POSITIVE OPENS, and zero is where the jaws MEET -- the same way round as
claw_gripper.py, so a sign means the same thing in both files.

Why any of this: docs/library-design-notes.md #1, #4, #8.
"""

from pybricks.parameters import Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.tools import StopWatch, wait


# ============================================================ LIFT FACTS ==

# EVERY NUMBER BELOW IS AT THE MOTOR, NOT AT THE JAWS. Measure the motor's
# number with the mechanism on the robot; the gearing cancels out.

LIFT_PORT = Port.C      # claw_gripper defaults to E, so both fit at once
LIFT_DIRECTION = Direction.COUNTERCLOCKWISE   # POSITIVE must mean OPENING  TUNE

OPEN_SPEED = 300        # deg/s
CLOSE_SPEED = 200       # deg/s -- slow enough not to slam the object
LIFT_SPEED = 150        # deg/s -- slowest: it is carrying now

HOME_EFFORT = 75        # % raw power, home() only. Too high strips gears.  TUNE
GRIP_TORQUE = 60       # mNm -- phase 1 squeeze. High crushes, low slips.  TUNE
LIFT_TORQUE = 200       # mNm -- phase 2. MUST exceed GRIP_TORQUE or the
                        # lift can never push past its own grip.            TUNE

READY_ANGLE = 120       # deg open -- wide enough for your BIGGEST object.  TUNE

GRIP_OVERSHOOT = 10     # deg past shut. Unreachable on purpose: the jaws never
GRIP_TARGET = -GRIP_OVERSHOOT       # arrive, so they never stop leaning in.

LIFT_TRAVEL = 75        # deg PAST CONTACT -- the lift itself. Not a position:
                        # raise until the object clears the mat.            TUNE

AIR_MARGIN = 15         # deg. Contact below this = we caught nothing. Must be
                        # under what your SMALLEST object holds open.       TUNE
LIFT_LOAD_MIN = 60      # mNm -- below this we are carrying nothing.        TUNE
SETTLE_MS = 150         # ms -- let the squeeze finish creeping in.         TUNE
GRIP_TIMEOUT_MS = 1500  # ms -- jammed. Give up instead of standing still.  TUNE


# ============================================================== HARDWARE ==

lift = Motor(LIFT_PORT, LIFT_DIRECTION)



# ================================================================= VERBS ==

def home():
    """Shut the jaws on NOTHING, call that zero, then open ready. Every run.

    The motor counts from wherever it was switched on, so after a crash or a
    battery swap that zero is garbage. Jaws meeting each other is a rigid stop
    that never lies -- and it costs no measuring at all.
    """
    lift.run_until_stalled(-CLOSE_SPEED, then=Stop.COAST,
                           duty_limit=HOME_EFFORT)
    wait(200)
    lift.reset_angle(0)
    lift.run_target(OPEN_SPEED, READY_ANGLE, then=Stop.COAST)


def grab():
    """Squeeze the object, then lift it. True if we are carrying something."""
    # PHASE 1 -- TORQUE. Aim past shut so we never arrive; lean in at
    # GRIP_TORQUE until the object stops us. One behaviour, any object.
    lift.control.limits(torque=GRIP_TORQUE)
    lift.run_target(CLOSE_SPEED, GRIP_TARGET, then=Stop.HOLD, wait=False)

    timer = StopWatch()
    wait(100)                          # let it get moving before asking
    while timer.time() < GRIP_TIMEOUT_MS:
        if lift.stalled() or lift.done():
            break
        wait(10)
    wait(SETTLE_MS)

    contact = lift.angle()             # THE DATUM. Only phase 1 can know it.
    if contact < AIR_MARGIN:
        return False                   # jaws met -- nothing between them

    # PHASE 2 -- ANGLE, relative to contact. The jaws are clamped, so this
    # travel levers the frame up instead. Needs more torque than the grip it
    # has to push past. Stop.HOLD is load-bearing: one motor holds BOTH the
    # squeeze and the height, and the limit stays high so it doesn't sag.
    #
    # NOT run_angle(). It is relative to the CONTROLLER'S REFERENCE, not to
    # angle(), and while we are squeezing those differ by the squeeze itself
    # (force = kp x that gap, ~17 deg at GRIP_TORQUE). run_angle would
    # overshoot by it, and by more for a softer object.
    lift.control.limits(torque=LIFT_TORQUE)
    lift.run_target(LIFT_SPEED, contact - LIFT_TRAVEL, then=Stop.HOLD)
    return holding()


def release():
    """Set the object down and open the jaws. Back to ready."""
    # +LIFT_TRAVEL walks the lift back off, landing near the contact point
    # whatever it was -- so this never needs to remember where the grip
    # stopped. "Near" is fine: the next move is an absolute one, so any slop
    # from the hold is wiped out rather than accumulated.
    lift.control.limits(torque=LIFT_TORQUE)
    lift.run_target(LIFT_SPEED, lift.angle() + LIFT_TRAVEL, then=Stop.HOLD)
    lift.control.limits(torque=GRIP_TORQUE)
    lift.run_target(OPEN_SPEED, READY_ANGLE, then=Stop.COAST)


# =============================================================== CHECKING ==

def lift_load(samples=5):
    """Average load in mNm. How hard, never which way."""
    # abs() because load() reads negative on some builds, and a loaded arm at
    # -80 must not look emptier than a bare one.
    total = 0
    for i in range(samples):
        total += abs(lift.load())
        wait(20)
    return total // samples


def holding():
    """Are we still carrying it? Once lifted, LOAD is the only witness.

    The angle test lives inside grab(), where contact still means something.
    Out here the arm is LIFT_TRAVEL past a contact point nobody remembers.

    ASK IT TWICE -- grab() answers here, this answers at the far end:

        lift.grab()
        drive_straight(600)
        if not lift.holding():
            print("lost it -- don't bother placing")
    """
    return lift_load() > LIFT_LOAD_MIN


def show_angle():
    """Print lift angle and load. Measure at THREE places, in this order:

        1. after home()                  -> about READY_ANGLE
        2. gripping your SMALLEST object -> AIR_MARGIN goes BELOW this
        3. lifted and carrying           -> LIFT_LOAD_MIN goes halfway between
                                            this and the same reading on air
    """
    print("lift angle:", lift.angle(), " load:", lift.load())
