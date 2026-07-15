"""my_lib_run.py — YOUR library (built D5–D7), engine: motor.run().

run() regulates each wheel's SPEED for free (deg/s, battery-proof), but the
wheels don't know about each other — the gyro glue that keeps them honest
is yours: speed = error x KP.

Contract (identical in all three engines): distances in mm, speeds in mm/s,
headings in ABSOLUTE degrees (frame set by the last reset_heading).

Self-contained — tune every constant right here in this file.
KEEP IN SYNC with my_lib_dc.py / my_lib_drivebase.py — same names, same order.
"""

from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.tools import StopWatch, wait

# ---------------------------------------------- robot facts (tune here) --
LEFT_DRIVE_PORT = Port.A                       # re-port a motor = edit one line
RIGHT_DRIVE_PORT = Port.E
LEFT_SENSOR_PORT = Port.B
RIGHT_SENSOR_PORT = Port.F
LEFT_DRIVE_DIR = Direction.COUNTERCLOCKWISE     # flip if your build mirrors
RIGHT_DRIVE_DIR = Direction.CLOCKWISE
WHEEL_DIAMETER = 88    # mm — roll the wheel 5 turns, divide by 5*pi
STRAIGHT_SPEED = 300   # mm/s — default cruise
LINE_SPEED = 120       # mm/s while following a line
APPROACH_SPEED = 100   # mm/s for wall touches / scoring approaches
LINE_THRESHOLD = 50    # midpoint of black/white reflection calib
BACKOFF_MM = 50        # measured back-off after a wall touch

# ---------------------------------------------------------------- hardware --
hub = PrimeHub()
left_motor = Motor(LEFT_DRIVE_PORT, LEFT_DRIVE_DIR)
right_motor = Motor(RIGHT_DRIVE_PORT, RIGHT_DRIVE_DIR)
left_eye = ColorSensor(LEFT_SENSOR_PORT)
right_eye = ColorSensor(RIGHT_SENSOR_PORT)

# ------------------------------------------------------------ engine knobs --
KP_HEAD = 6           # deg/s of wheel-speed correction per deg heading error
KP_TURN = 3.5         # deg/s of wheel speed per deg of turn remaining
KP_LINE = 4           # deg/s per reflection point off the edge
KD_LINE = 12          # deg/s per reflection point of CHANGE — calms the wiggle  TUNE
MIN_TURN_SPEED = 60   # deg/s — slow enough to never coast past  TUNE
MAX_TURN_SPEED = 400  # deg/s
TURN_TOL = 2          # deg — "close enough"


# ------------------------------------------------------------ unit helpers --
def _mm_to_deg(mm):
    return mm * 360 / (3.142 * WHEEL_DIAMETER)


def _mmps_to_degps(mmps):
    return mmps * 360 / (3.142 * WHEEL_DIAMETER)


# ------------------------------------------------------------------- verbs --
def reset_heading(heading_deg=0):
    """Zero (or set) the gyro heading frame."""
    hub.imu.reset_heading(heading_deg)


def drive_straight(distance_mm, speed=None):
    """Gyro-held straight drive. Negative distance = backward."""
    speed = speed if speed is not None else STRAIGHT_SPEED
    wheel_speed = _mmps_to_degps(speed)
    sign = 1 if distance_mm >= 0 else -1
    target_deg = _mm_to_deg(abs(distance_mm))
    left_motor.reset_angle(0)
    right_motor.reset_angle(0)
    heading0 = hub.imu.heading()
    while (abs(left_motor.angle()) + abs(right_motor.angle())) / 2 < target_deg:
        steer = KP_HEAD * (hub.imu.heading() - heading0)  # speed = error x KP
        left_motor.run(sign * wheel_speed - steer)
        right_motor.run(sign * wheel_speed + steer)
        wait(10)
    left_motor.hold()
    right_motor.hold()


def turn_to(heading_deg):
    """Turn to an ABSOLUTE heading (gyro frame set by the last reset)."""
    error = heading_deg - hub.imu.heading()
    while abs(error) > TURN_TOL:
        # Speed SHRINKS with the error — big error turns fast, small error
        # creeps in, so the robot never coasts past the target.
        speed = min(MAX_TURN_SPEED, max(MIN_TURN_SPEED, KP_TURN * abs(error)))
        if error > 0:                       # positive heading = clockwise
            left_motor.run(speed)
            right_motor.run(-speed)
        else:
            left_motor.run(-speed)
            right_motor.run(speed)
        wait(5)
        error = heading_deg - hub.imu.heading()
    left_motor.hold()
    right_motor.hold()


def drive_to_wall(speed=None, timeout_ms=4000):
    """Wall touch WITHOUT a distance sensor. True on stall, False on timeout."""
    speed = speed if speed is not None else APPROACH_SPEED
    wheel_speed = _mmps_to_degps(speed)
    watch = StopWatch()
    left_motor.run(wheel_speed)
    right_motor.run(wheel_speed)
    while True:
        if watch.time() > timeout_ms:
            left_motor.stop()
            right_motor.stop()
            return False
        # run() keeps the speed controller on, so stalled() works for free —
        # the controller knows it can't reach its target. (dc() can't do this.)
        if watch.time() > 300 and left_motor.stalled() and right_motor.stalled():
            left_motor.stop()
            right_motor.stop()
            return True
        wait(10)


def wall_square(new_heading=0, backoff=None):
    """Square onto a wall, reset the gyro, back off a measured distance."""
    drive_to_wall()
    wait(250)                               # settle flat against the wall
    reset_heading(new_heading)
    drive_straight(-(backoff if backoff is not None else BACKOFF_MM))


def follow_line(sensor, distance_mm, speed=None):
    """PD line follow on one sensor edge for an encoder distance."""
    speed = speed if speed is not None else LINE_SPEED
    base = _mmps_to_degps(speed)
    target_deg = _mm_to_deg(distance_mm)
    left_motor.reset_angle(0)
    right_motor.reset_angle(0)
    last_error = 0
    while (abs(left_motor.angle()) + abs(right_motor.angle())) / 2 < target_deg:
        error = sensor.reflection() - LINE_THRESHOLD
        turn = KP_LINE * error + KD_LINE * (error - last_error)  # PD: P + D
        last_error = error
        left_motor.run(base + turn)
        right_motor.run(base - turn)
        wait(10)
    left_motor.hold()
    right_motor.hold()


def square_on_line(speed=60):
    """Creep until EACH eye sees the line, holding that side's wheel — pivots square."""
    creep = _mmps_to_degps(speed)
    left_done = right_done = False
    left_motor.run(creep)
    right_motor.run(creep)
    while not (left_done and right_done):
        if not left_done and left_eye.reflection() < LINE_THRESHOLD:
            left_motor.hold()
            left_done = True
        if not right_done and right_eye.reflection() < LINE_THRESHOLD:
            right_motor.hold()
            right_done = True
        wait(5)
