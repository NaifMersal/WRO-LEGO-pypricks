"""movements.py -- how your robot DRIVES. Wheels and one eye, nothing else.

    from movements import *      # only one of its kind, so a star import is safe

    reset_heading(0)
    drive_straight(300)
    turn_to(90)
    find_line()

RULES OF THE ROAD
    distances in mm         drive_straight(300) = 30 cm
    speeds in mm/s          drive_straight(300, speed=150)
    headings are ABSOLUTE   turn_to(90) means FACE 90, not "spin 90 more"
    to, or by               turn_to(90) faces 90. turn_by(90) spins 90 MORE.

ONE ZERO, AND ONLY reset_heading() MOVES IT
    Every turn_to() is measured from the zero you set. Nothing else in this
    file is allowed to move that zero -- if a verb moved it halfway through a
    mission, every turn after it would aim at the wrong place.

THE SIX VERBS THAT RUN THE ANCHOR
    reset_heading(h)      set the zero, once, placed straight
    drive_straight(mm)    forward, or backward if mm is negative
    turn_to(h)            FACE this heading
    turn_by(a)            spin this many degrees MORE
    find_line()           creep until the eye finds a line -- CHECK what it returns
    follow_line(mm)       ride the edge of the line this far

    heading()  and  show_eye()  don't move the robot -- they let you SEE what it
    thinks, which is how you tune. The two colour verbs at the foot of the file
    are STRETCH -- you score ~135 without ever naming a colour.

Everything you might change is in ROBOT FACTS, at the top.
Why any of this: docs/library-design-notes.md #1, #7, #8.
"""

from pybricks.hubs import PrimeHub
from pybricks.parameters import Color, Direction, Port   # Color re-exported, so
from pybricks.pupdevices import ColorSensor, Motor       # missions can say
from pybricks.robotics import DriveBase                  # find_color(Color.RED)
from pybricks.tools import wait


# =========================================================== ROBOT FACTS ==
# Measure these on YOUR robot.

LEFT_MOTOR_PORT = Port.F
RIGHT_MOTOR_PORT = Port.B
EYE_PORT = Port.D       # one colour sensor. C and E go to the grippers,
                        # leaving A -- a second eye OR a third mechanism.

LEFT_DIRECTION = Direction.COUNTERCLOCKWISE   # flip if the robot drives backward
RIGHT_DIRECTION = Direction.CLOCKWISE

WHEEL_DIAMETER = 88     # mm -- roll 5 turns, measure, divide by 5 x 3.14   TUNE
AXLE_TRACK = 128        # mm -- between the two wheel contact patches       TUNE

CRUISE_SPEED = 300      # mm/s -- normal driving
SLOW_SPEED = 100        # mm/s -- hunting for a line or a colour
LINE_SPEED = 120        # mm/s -- while following a line

LINE_THRESHOLD = 50     # halfway between your black and white readings     TUNE
KP_LINE = 1.2           # how hard to steer back to the line                TUNE

SEARCH_MM = 400         # how far to hunt before giving up                  TUNE


# ============================================================== HARDWARE ==

hub = PrimeHub()                          # for the speaker, the display, the button
left_motor = Motor(LEFT_MOTOR_PORT, LEFT_DIRECTION)
right_motor = Motor(RIGHT_MOTOR_PORT, RIGHT_DIRECTION)
eye = ColorSensor(EYE_PORT)

robot = DriveBase(left_motor, right_motor, WHEEL_DIAMETER, AXLE_TRACK)
robot.use_gyro(True)                      # the gyro keeps us straight
robot.settings(straight_speed=CRUISE_SPEED)


# ========================================================= DRIVING VERBS ==

def reset_heading(heading=0):
    """Declare 'the way I face right now is <heading>'. Run once, placed straight.

    This is the ONLY verb that moves the zero. robot.reset() would also move it
    -- which is why no other verb in this file calls it.
    """
    robot.reset(angle=heading)


def drive_straight(distance_mm, speed=CRUISE_SPEED):
    """Drive straight. Negative distance = backward."""
    robot.settings(straight_speed=speed)
    robot.straight(distance_mm)

def turn_to(heading):
    """Turn until the robot FACES this heading. turn_to(90) twice leaves you at 90."""
    # absolute=True aims at the zero, not at where we happen to be pointing.
    # Drop it and a hot corner is added to the next one instead of erased.
    robot.turn(heading, absolute=True)


def turn_by(angle):
    """Spin this many degrees MORE, from wherever we face now. turn_by(90) twice = 180.

    Use it when the mission says "quarter turn left"; use turn_to() when it says
    "face the stage". Four turn_by(90)s pile up their errors -- four turn_to()s
    do not, which is why the anchor run is written in turn_to().
    """
    robot.turn(angle)


def heading():
    """What are we facing right now, counted from the zero reset_heading() set?"""
    return robot.angle()

# ======================================================== FINDING THE MAT ==
# Everything ABOVE this line adds error. Everything below it takes error away.

def find_line(max_mm=SEARCH_MM, speed=SLOW_SPEED):
    """Creep forward until the eye sees a line. True if found -- always check it."""
    start = robot.distance()      # remember the odometer; do NOT robot.reset()
    robot.drive(speed, 0)
    while abs(robot.distance() - start) < max_mm:
        if eye.reflection() < LINE_THRESHOLD:
            robot.stop()
            return True
        wait(5)
    robot.stop()
    return False


def follow_line(distance_mm, speed=LINE_SPEED):
    """Ride the EDGE of the line for a distance. One eye follows edges, not middles."""
    start = robot.distance()      # remember the odometer; do NOT robot.reset()
    while abs(robot.distance() - start) < abs(distance_mm):
        error = eye.reflection() - LINE_THRESHOLD
        robot.drive(speed, KP_LINE * error)
        wait(10)
    robot.stop()


# ============================================================ CALIBRATION ==

def show_eye():
    """Print what the eye sees. Move the robot by hand, on the REAL mat.

    White -> write the number down. The line -> write that down.
    LINE_THRESHOLD goes halfway between.
    """
    while True:
        print("reflection:", eye.reflection(), "  colour:", eye.color())
        wait(500)


# ================================================================ STRETCH ==
#   NOTHING BELOW THIS LINE IS NEEDED FOR THE ANCHOR RUN.
# ~135 points -- instruments, cables, bonus-by-avoidance, microphone -- without
# ever naming a colour. Reflection barely moves; colour depends on the bulbs
# above the table. Lock the run above the line first. These two are for the
# fixed green/red notes (D24). Why: library-design-notes.md #7.

def find_color(wanted, max_mm=SEARCH_MM, speed=SLOW_SPEED):
    """Creep forward until the eye sees this colour -- find_color(Color.RED).

    Run show_eye() on the real mat under the real lights before trusting this.
    """
    start = robot.distance()      # remember the odometer; do NOT robot.reset()
    robot.drive(speed, 0)
    while abs(robot.distance() - start) < max_mm:
        if eye.color() == wanted:
            robot.stop()
            return True
        wait(5)
    robot.stop()
    return False


def follow_line_to_color(wanted, max_mm=SEARCH_MM, speed=LINE_SPEED):
    """Follow the line until the eye lands on a colour. True if we got there.

    Better than a fixed distance: the colour tells you that you ARRIVED, so a
    bit of wheel slip costs you nothing.
    """
    start = robot.distance()      # remember the odometer; do NOT robot.reset()
    while abs(robot.distance() - start) < max_mm:
        if eye.color() == wanted:
            robot.stop()
            return True
        error = eye.reflection() - LINE_THRESHOLD
        robot.drive(speed, KP_LINE * error)
        wait(10)
    robot.stop()
    return False
