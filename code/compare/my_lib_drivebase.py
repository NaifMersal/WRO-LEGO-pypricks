"""my_lib_drivebase.py — the SAME library, engine: DriveBase (the D8 shortcut).

Same seven verbs, now driving Pybricks' professional controller: gyro-fused,
battery-proof, ramped. Count the lines that disappeared — then notice which
verb did NOT: DriveBase has no per-wheel verb, so square_on_line still drops
to the motors. The library keeps what the shortcut can't do.

Contract (identical in all three engines): distances in mm, speeds in mm/s,
headings in ABSOLUTE degrees (frame set by the last reset_heading).

Self-contained — tune every constant right here in this file.
KEEP IN SYNC with my_lib_run.py / my_lib_dc.py — same names, same order.
"""

from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait

# ---------------------------------------------- robot facts (tune here) --
LEFT_DRIVE_PORT = Port.A                       # re-port a motor = edit one line
RIGHT_DRIVE_PORT = Port.E
LEFT_SENSOR_PORT = Port.B
RIGHT_SENSOR_PORT = Port.F
LEFT_DRIVE_DIR = Direction.COUNTERCLOCKWISE     # flip if your build mirrors
RIGHT_DRIVE_DIR = Direction.CLOCKWISE
WHEEL_DIAMETER = 88    # mm — roll the wheel 5 turns, divide by 5*pi
AXLE_TRACK = 145       # mm — distance between wheel CONTACT centers
STRAIGHT_SPEED = 300   # mm/s — default cruise
STRAIGHT_ACCEL = 450   # mm/s^2
TURN_RATE = 150        # deg/s
TURN_ACCEL = 300       # deg/s^2
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

drive = DriveBase(left_motor, right_motor, WHEEL_DIAMETER, AXLE_TRACK)
drive.use_gyro(True)
drive.settings(
    straight_speed=STRAIGHT_SPEED,
    straight_acceleration=STRAIGHT_ACCEL,
    turn_rate=TURN_RATE,
    turn_acceleration=TURN_ACCEL,
)

# ------------------------------------------------------- line-follow gains --
KP_LINE = 1.2         # steering rate per reflection point off the edge
KD_LINE = 4.0         # steering rate per reflection point of CHANGE  TUNE
# (drive.settings above handles ramp + gyro — no engine-compensation knobs.)


# ------------------------------------------------------------ unit helpers --
def _mmps_to_degps(mmps):
    # DriveBase converts units everywhere else — only the per-wheel
    # square_on_line still needs this by hand.
    return mmps * 360 / (3.142 * WHEEL_DIAMETER)


# ------------------------------------------------------------------- verbs --
def reset_heading(heading_deg=0):
    """Zero (or set) the gyro heading frame."""
    hub.imu.reset_heading(heading_deg)


def drive_straight(distance_mm, speed=None):
    """Gyro-held straight drive. Negative distance = backward."""
    if speed is not None:
        s = drive.settings()
        drive.settings(straight_speed=speed)
        drive.straight(distance_mm)
        drive.settings(straight_speed=s[0])
    else:
        drive.straight(distance_mm)


def turn_to(heading_deg):
    """Turn to an ABSOLUTE heading."""
    drive.turn(heading_deg)


def drive_to_wall(speed=None, timeout_ms=4000):
    """Wall touch WITHOUT a distance sensor. True on stall, False on timeout."""
    speed = speed if speed is not None else APPROACH_SPEED
    watch = StopWatch()
    drive.drive(speed, 0)
    while not drive.stalled():              # stall detection: built in
        if watch.time() > timeout_ms:
            drive.stop()
            return False
        wait(10)
    drive.stop()
    return True


def wall_square(new_heading=0, backoff=None):
    """Square onto a wall, reset the gyro, back off a measured distance."""
    drive_to_wall()
    wait(250)                               # settle flat against the wall
    reset_heading(new_heading)
    drive.straight(-(backoff if backoff is not None else BACKOFF_MM))


def follow_line(sensor, distance_mm, speed=None):
    """PD line follow on one sensor edge for an encoder distance."""
    speed = speed if speed is not None else LINE_SPEED
    drive.reset()
    last_error = 0
    while abs(drive.distance()) < distance_mm:
        error = sensor.reflection() - LINE_THRESHOLD
        turn = KP_LINE * error + KD_LINE * (error - last_error)  # PD
        last_error = error
        drive.drive(speed, turn)
        wait(10)
    drive.stop()


def square_on_line(speed=60):
    """Creep until EACH eye sees the line, holding that side's wheel — pivots square."""
    # DriveBase can't move one wheel — this verb stays exactly as you built it.
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
