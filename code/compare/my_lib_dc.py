"""my_lib_dc.py — the SAME library, engine: motor.dc() (what's under the hood).

dc() sets raw motor power — duty %. Duty is NOT speed: a fresh battery, a
heavy load, a carpet seam all change what the same duty does. Everything
run() and DriveBase gave you for free is hand-rolled below.

Read this file to understand your tools. Do NOT compete on it — the bootcamp
keeps missions on run()/DriveBase on purpose.

Contract (identical in all three engines): distances in mm, speeds in mm/s,
headings in ABSOLUTE degrees (frame set by the last reset_heading).

Self-contained — tune every constant right here in this file.
KEEP IN SYNC with my_lib_run.py / my_lib_drivebase.py — same names, same order.
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
CREEP_SPEED = 60       # mm/s while squaring on a line
LINE_THRESHOLD = 50    # midpoint of black/white reflection calib
BACKOFF_MM = 50        # measured back-off after a wall touch
STALL_GRACE_MS = 300   # ignore the standing start before believing a stall

# ---------------------------------------------------------------- hardware --
hub = PrimeHub()
left_motor = Motor(LEFT_DRIVE_PORT, LEFT_DRIVE_DIR)
right_motor = Motor(RIGHT_DRIVE_PORT, RIGHT_DRIVE_DIR)
left_eye = ColorSensor(LEFT_SENSOR_PORT)
right_eye = ColorSensor(RIGHT_SENSOR_PORT)

# ----------------------------------- engine knobs (the ones dc() hands YOU) --
DUTY_PER_MMS = 0.14   # duty % per mm/s ~ 100 / (970 deg/s * 276 mm / 360)
#                       drifts with battery + load — that's the dc() lesson  TUNE
MIN_DUTY = 12         # below this, friction wins and nothing moves  TUNE
MAX_DUTY = 90         # headroom left for the steering correction
RAMP_STEP = 3         # duty % added per 10 ms tick = hand-rolled acceleration
PRESS_DUTY = 20       # gentle lean while squaring on a wall
KP_HEAD = 2.5         # duty % per deg heading error  TUNE
KP_TURN = 1.2         # duty % per deg of turn remaining  TUNE
KP_LINE = 0.5         # duty % per reflection point off the edge  TUNE
KD_LINE = 1.5         # duty % per reflection point of CHANGE  TUNE
TURN_TOL = 2          # deg — "close enough"
STALL_SPEED = 20      # deg/s measured — below this = "stalled"  TUNE


# ------------------------------------------------------------ unit helpers --
def mm_to_deg(mm):
    return mm * 360 / (3.142 * WHEEL_DIAMETER)


def mmps_to_duty(mmps):
    return mmps * DUTY_PER_MMS              # a GUESS, not a promise


# ------------------------------------------------------------------- verbs --
def reset_heading(heading_deg=0):
    """Zero (or set) the gyro heading frame."""
    hub.imu.reset_heading(heading_deg)


def drive_straight(distance_mm, speed=STRAIGHT_SPEED):
    """Gyro-held straight drive. Negative distance = backward."""
    base = min(MAX_DUTY, max(MIN_DUTY, mmps_to_duty(speed)))
    sign = 1 if distance_mm >= 0 else -1
    target_deg = mm_to_deg(abs(distance_mm))
    left_motor.reset_angle(0)
    right_motor.reset_angle(0)
    heading0 = hub.imu.heading()
    duty = 0
    while (abs(left_motor.angle()) + abs(right_motor.angle())) / 2 < target_deg:
        duty = min(base, duty + RAMP_STEP)  # ramp up — no ramp = wheel chirp
        steer = KP_HEAD * (hub.imu.heading() - heading0)  # duty = error x KP
        # flip steer's sign if the robot fights its own correction  TUNE
        left_motor.dc(sign * duty - steer)
        right_motor.dc(sign * duty + steer)
        wait(10)
    left_motor.brake()
    right_motor.brake()


def turn_to(heading_deg):
    """Turn TO an absolute heading — a compass, not a steering wheel.
    turn_to(90) twice leaves you at 90, not 180."""
    while True:
        error = heading_deg - hub.imu.heading()
        if abs(error) < TURN_TOL:
            break
        # MIN_DUTY floor: pure error x KP fades below static friction near the
        # target and the turn stalls a few degrees short — forever. The floor
        # is the honest fix (no I-term in this bootcamp).
        duty = min(MAX_DUTY, max(MIN_DUTY, KP_TURN * abs(error)))
        if error > 0:                       # positive heading = clockwise
            left_motor.dc(duty)
            right_motor.dc(-duty)
        else:
            left_motor.dc(-duty)
            right_motor.dc(duty)
        wait(5)
    left_motor.brake()
    right_motor.brake()
    wait(150)                               # settle — brake is not hold


def drive_to_wall(speed=APPROACH_SPEED, timeout_ms=4000):
    """Wall touch WITHOUT a distance sensor. True on stall, False on timeout."""
    duty = max(MIN_DUTY, mmps_to_duty(speed))
    watch = StopWatch()
    left_motor.dc(duty)
    right_motor.dc(duty)
    while watch.time() < timeout_ms:
        # stalled() means nothing under dc() — no controller, no target.
        # The encoder is the sensor: measured speed collapsing = the wall.
        if (watch.time() > STALL_GRACE_MS
                and abs(left_motor.speed()) < STALL_SPEED
                and abs(right_motor.speed()) < STALL_SPEED):
            left_motor.brake()
            right_motor.brake()
            return True
        wait(10)
    left_motor.brake()
    right_motor.brake()
    return False


def wall_square(new_heading=0, backoff=BACKOFF_MM):
    """Square onto a wall, reset the gyro, back off a measured distance."""
    duty = max(MIN_DUTY, mmps_to_duty(APPROACH_SPEED))
    watch = StopWatch()
    left_motor.dc(duty)
    right_motor.dc(duty)
    left_done = right_done = False
    while not (left_done and right_done):
        if watch.time() > 4000:
            break
        if watch.time() > STALL_GRACE_MS:
            # Each wheel that reaches the wall drops to a gentle lean so it
            # keeps pressing while the other wheel catches up = square.
            if not left_done and abs(left_motor.speed()) < STALL_SPEED:
                left_motor.dc(PRESS_DUTY)
                left_done = True
            if not right_done and abs(right_motor.speed()) < STALL_SPEED:
                right_motor.dc(PRESS_DUTY)
                right_done = True
        wait(10)
    wait(250)                               # settle flat against the wall
    reset_heading(new_heading)
    left_motor.brake()
    right_motor.brake()
    drive_straight(-backoff)


def follow_line(sensor, distance_mm, speed=LINE_SPEED):
    """PD line follow on one sensor edge for an encoder distance."""
    base = max(MIN_DUTY, mmps_to_duty(speed))
    target_deg = mm_to_deg(abs(distance_mm))
    left_motor.reset_angle(0)
    right_motor.reset_angle(0)
    last_error = 0
    while (abs(left_motor.angle()) + abs(right_motor.angle())) / 2 < target_deg:
        error = sensor.reflection() - LINE_THRESHOLD
        steer = KP_LINE * error + KD_LINE * (error - last_error)  # PD — raw duty:
        last_error = error                  # visibly slows on seams (duty != speed)
        left_motor.dc(min(MAX_DUTY, max(-MAX_DUTY, base + steer)))
        right_motor.dc(min(MAX_DUTY, max(-MAX_DUTY, base - steer)))
        wait(10)
    left_motor.brake()
    right_motor.brake()


def square_on_line(speed=CREEP_SPEED):
    """Creep until EACH eye sees the line, holding that side's wheel — pivots square."""
    creep = max(MIN_DUTY, mmps_to_duty(speed))
    left_done = right_done = False
    left_motor.dc(creep)
    right_motor.dc(creep)
    while not (left_done and right_done):
        if not left_done and left_eye.reflection() < LINE_THRESHOLD:
            left_motor.hold()               # hold() is a controller command —
            left_done = True                # it works fine even from dc()
        if not right_done and right_eye.reflection() < LINE_THRESHOLD:
            right_motor.hold()
            right_done = True
        wait(5)
