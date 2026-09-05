"""grip_test.py -- find your claw's real numbers, on the bench, with data.

        IF I DO THE EXACT SAME THING TEN TIMES,
        HOW MUCH DOES THE ANSWER WANDER?

That is a SPREAD, and show_angle()'s one reading can never show you one.

HOW TO USE IT
    1. Put the object you actually carry in the jaws' path.
    2. Run this file.
    3. Write three numbers into claw_gripper.py's CLAW FACTS:

        EMPTY_ANGLE     from the EMPTY test at the top
        GRIP_LOAD_MIN   about half the holding load from the ten-grab table
        GRIP_TORQUE     raise if the object slips, lower if the gears crunch

    4. Run it again. Tuning is a loop, not a step.

BIG_ANGLE_MAX IS NOT HERE. Telling a big note from a small one needs the robot
driving, so it lives in object_test.py test_size() with the rest of the
note measurements.

GRIP_ANGLE is NOT one of them -- claw_gripper.py derives it from EMPTY_ANGLE.
Why this file exists: docs/library-design-notes.md #5.
"""

from pybricks.parameters import Stop
from pybricks.tools import wait

import claw_gripper as gripper

# The motor itself, so Test 2 can drive it the old way for comparison.
motor = gripper.claw


# ============================================================ TEST FACTS ==

TRIES = 10              # grabs per test -- fewer than 8 and a spread lies
COMPARE_TRIES = 5       # grabs per column in the side-by-side
REST_MS = 600           # pause between grabs, so nothing is still moving

STALL_EFFORT = 50       # the duty_limit the old stall-based grab() used
CLOSE_EFFORT = 40       # gentle -- measure_empty() presses plastic on plastic


# ================================================================= TOOLS ==

def spread(values):
    """Smallest, biggest, and the gap between them."""
    return min(values), max(values), max(values) - min(values)


def average(values):
    return sum(values) // len(values)


def report(name, angles, loads):
    """Print one experiment as a table, then its verdict. Returns the spread."""
    print("")
    print("---", name, "---")
    print("try   angle   load")
    for i in range(len(angles)):
        print(" ", i + 1, "   ", angles[i], "   ", loads[i])

    low, high, gap = spread(angles)
    print("angle:", low, "to", high, " spread:", gap, "deg")
    print("load :", average(loads), "mNm average")

    if gap <= 10:
        print("VERDICT: tight. You can build a run on this.")
    elif gap <= 25:
        print("VERDICT: loose. Check the claw for rock in its mounting.")
    else:
        print("VERDICT: too wide to trust. Fix the build before the code.")
    return gap


# ================================================================= TESTS ==

def measure_empty():
    """Close on NOTHING until the jaws physically MEET. That is EMPTY_ANGLE.

    Note it does NOT call grab(): grab() drives to GRIP_ANGLE and, with empty
    jaws, simply arrives -- handing back the target you already set.
    """
    print("=== EMPTY JAWS -- take the object OUT ===")
    print("starting in 5 seconds...")
    wait(5000)

    gripper.home()
    motor.run_until_stalled(gripper.CLOSE_SPEED, then=Stop.COAST,
                            duty_limit=CLOSE_EFFORT)
    angle = motor.angle()
    gripper.release()

    print("EMPTY_ANGLE is about", angle, "-- where the jaws MEET")
    print("-> write that one number into CLAW FACTS; GRIP_ANGLE follows")
    return angle


def test_repeatability():
    """The main event: the same grab, TRIES times. Under ~10 deg spread is good."""
    print("")
    print("=== WITH THE OBJECT -- put it in the jaws now ===")
    print("starting in 5 seconds...")
    wait(5000)

    angles = []
    loads = []
    for i in range(TRIES):
        gripper.home()
        caught = gripper.grab()
        angles.append(motor.angle())
        loads.append(gripper.grip_load())
        if not caught:
            print("  (try", i + 1, "says it caught AIR -- is the object there?)")
        gripper.release()
        wait(REST_MS)

    return report("TORQUE GRAB, " + str(TRIES) + " tries", angles, loads)


def stall_grab():
    """Grab the OLD way -- stall in and hold where it stopped.

    Here ONLY for the comparison. Do not copy this into your gripper file.
    """
    motor.run_until_stalled(gripper.CLOSE_SPEED, then=Stop.HOLD,
                            duty_limit=STALL_EFFORT)


def test_comparison():
    """Torque against stalling, same object, same claw, same afternoon."""
    print("")
    print("=== TORQUE vs STALL ===")

    torque_angles = []
    torque_loads = []
    for i in range(COMPARE_TRIES):
        gripper.home()
        gripper.grab()
        torque_angles.append(motor.angle())
        torque_loads.append(gripper.grip_load())
        gripper.release()
        wait(REST_MS)

    stall_angles = []
    stall_loads = []
    for i in range(COMPARE_TRIES):
        gripper.home()
        stall_grab()
        stall_angles.append(motor.angle())
        stall_loads.append(gripper.grip_load())
        gripper.release()
        wait(REST_MS)

    t_gap = report("BY TORQUE", torque_angles, torque_loads)
    s_gap = report("BY STALLING", stall_angles, stall_loads)

    print("")
    print("torque spread:", t_gap, "deg   stall spread:", s_gap, "deg")
    if s_gap > t_gap:
        print("Stalling wandered more. That is the whole argument.")
    else:
        print("Close today. Run it again on a HALF-FLAT battery.")


# ================================================================== MAIN ==

def main():
    print("GRIP TEST -- keep your hands clear of the jaws.")
    measure_empty()
    test_repeatability()
    test_comparison()
    print("")
    print("Done. Write your numbers into claw_gripper.py, then run me again.")


main()
