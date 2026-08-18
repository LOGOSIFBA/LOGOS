import time
import math

GREEN_VALUES = ("green", "cyan")

def is_clear_intersection(digital):
    return all(digital)

def is_left_90_candidate(digital):
    return digital[0] and digital[1] and not digital[3] and not digital[4]

def is_green(color):
    return color in GREEN_VALUES

def detect_color_marking(color_sensor_r, color_sensor_l, duration=0.15):
    start_time = time.monotonic()

    right_green_count = 0
    left_green_count = 0

    while time.monotonic() - start_time < duration:
        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r):
            right_green_count += 1

        if is_green(color_l):
            left_green_count += 1

        time.sleep(0.01)

    right_confirmed = right_green_count >= 2
    left_confirmed = left_green_count >= 2

    if right_confirmed and left_confirmed:
        return "180"

    if left_confirmed and not right_confirmed:
        return "LEFT"

    if right_confirmed and not left_confirmed:
        return "RIGHT"

    return None

def is_right_90_candidate(digital):
    return digital[3] and digital[4] and not digital[0] and not digital[1]

def is_gap(reading):
    return not reading["line_detected"]

def update_odometry_motors(odometry, motors):
    right_data = motors.right.get_position_telemetry()
    left_data = motors.left.get_position_telemetry()

    right_deg = right_data["position_deg"]
    left_deg = left_data["position_deg"]

    odometry.update(right_deg, left_deg)

def turn_left(driver_r, driver_l, motors, odometry, target_angle_rad):
    update_odometry_motors(odometry, motors)
    start_theta = odometry.theta

    while True:
        driver_l.set_speed(30)
        driver_r.set_speed(-30)

        update_odometry_motors(odometry, motors)

        turned_angle = odometry.angle_difference_rad(odometry.theta, start_theta)

        if turned_angle >= target_angle_rad:
            break

        time.sleep(0.01)

    driver_r.stop()
    driver_l.stop()

def turn_right(driver_r, driver_l, motors, odometry, target_angle_rad):
    update_odometry_motors(odometry, motors)
    start_theta = odometry.theta

    while True:
        driver_l.set_speed(-30)
        driver_r.set_speed(30)

        update_odometry_motors(odometry, motors)

        turned_angle = odometry.angle_difference_rad(odometry.theta, start_theta)

        if turned_angle <= -target_angle_rad:
            break

        time.sleep(0.01)

    driver_r.stop()
    driver_l.stop()

def move_straight_for(driver_r, driver_l, motors, odometry, duration, speed):
    start_time = time.monotonic()

    while time.monotonic() - start_time < duration:
        driver_l.set_speed(speed)
        driver_r.set_speed(speed)

        update_odometry_motors(odometry, motors)

        time.sleep(0.01)

    driver_r.stop()
    driver_l.stop()

def center_stays_on_line_during_short_forward(driver_r, driver_l, motors, line_sensor, odometry):
    start_time = time.monotonic()

    while time.monotonic() - start_time < 0.25:
        driver_l.set_speed(30)
        driver_r.set_speed(30)

        update_odometry_motors(odometry, motors)

        reading = line_sensor.get_data()
        digital = reading["digital"]

        if not digital[2]:
            driver_r.stop()
            driver_l.stop()
            return False

        time.sleep(0.01)

    driver_r.stop()
    driver_l.stop()
    return True

def handle_intersection(driver_r, driver_l, motors, odometry):
    move_straight_for(driver_r, driver_l, motors, odometry, 0.35, 35)

def handle_left_candidate(driver_r, driver_l, motors, line_sensor, odometry):
    center_stayed = center_stays_on_line_during_short_forward(driver_r, driver_l, motors, line_sensor, odometry)

    if center_stayed:
        handle_intersection(driver_r, driver_l, motors, odometry)
    else:
        turn_left(driver_r, driver_l, motors, odometry, math.radians(90))

def handle_right_candidate(driver_r, driver_l, motors, line_sensor, odometry):
    center_stayed = center_stays_on_line_during_short_forward(driver_r, driver_l, motors, line_sensor, odometry)

    if center_stayed:
        handle_intersection(driver_r, driver_l, motors, odometry)
    else:
        turn_right(driver_r, driver_l, motors, odometry, math.radians(90))

def handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
    if color_marking == "180":
        handle_180(driver_r, driver_l, motors, odometry)
        return True

    if color_marking == "LEFT":
        handle_color_90_left(driver_r, driver_l, motors, odometry)
        return True

    if color_marking == "RIGHT":
        handle_color_90_right(driver_r, driver_l, motors, odometry)
        return True

    return False

def follow_line(driver_r, driver_l, reading, pid, base_speed):
    position = reading["position"]

    correction = pid.calculate(position)

    left_speed = base_speed + correction
    right_speed = base_speed - correction

    left_speed = max(-50, min(50, left_speed))
    right_speed = max(-50, min(50, right_speed))

    driver_l.set_speed(left_speed)
    driver_r.set_speed(right_speed)

def try_cross_gap(driver_r, driver_l, motors, line_sensor, odometry):
    start_time = time.monotonic()

    while time.monotonic() - start_time < 3.0:
        driver_l.set_speed(30)
        driver_r.set_speed(30)

        update_odometry_motors(odometry, motors)

        reading = line_sensor.get_data()

        if reading["line_detected"]:
            driver_r.stop()
            driver_l.stop()
            return True

        time.sleep(0.01)

    forward_time = time.monotonic() - start_time

    move_straight_for(driver_r, driver_l, motors, odometry, forward_time, -30)
    return False

def is_obstacle(distance_sensor):
    distance = distance_sensor.get_distance_cm()

    if distance is None:
        return False

    return distance < 15

def handle_lost_line(driver_r, driver_l, motors, line_sensor, last_position, odometry):
    center_count = 0

    if last_position < 0:
        left_speed = 15
        right_speed = 30
    else:
        left_speed = 30
        right_speed = 15

    while True:
        driver_l.set_speed(left_speed)
        driver_r.set_speed(right_speed)

        update_odometry_motors(odometry, motors)

        reading = line_sensor.get_data()
        digital = reading["digital"]

        if reading["line_detected"] and digital[2]:
            center_count += 1
        else:
            center_count = 0

        if center_count >= 3:
            driver_r.stop()
            driver_l.stop()
            return True

        time.sleep(0.01)

def handle_obstacle(driver_r, driver_l, motors, odometry):
    driver_r.stop()
    driver_l.stop()
    time.sleep(0.2)

    move_straight_for(driver_r, driver_l, motors, odometry, 0.15, -20)

    turn_right(driver_r, driver_l, motors, odometry, math.radians(90))
    move_straight_for(driver_r, driver_l, motors, odometry, 0.45, 30)

    turn_left(driver_r, driver_l, motors, odometry, math.radians(90))
    move_straight_for(driver_r, driver_l, motors, odometry, 0.50, 30)

    turn_left(driver_r, driver_l, motors, odometry, math.radians(90))
    move_straight_for(driver_r, driver_l, motors, odometry, 0.45, 30)

    turn_right(driver_r, driver_l, motors, odometry, math.radians(90))
    time.sleep(0.1)

def handle_180(driver_r, driver_l, motors, odometry):
    driver_r.stop()
    driver_l.stop()
    turn_right(driver_r, driver_l, motors, odometry, math.radians(180))

def handle_color_90_left(driver_r, driver_l, motors, odometry):
    driver_r.stop()
    driver_l.stop()
    turn_left(driver_r, driver_l, motors, odometry, math.radians(90))
    move_straight_for(driver_r, driver_l, motors, odometry, 0.2, 30)

def handle_color_90_right(driver_r, driver_l, motors, odometry):
    driver_r.stop()
    driver_l.stop()
    turn_right(driver_r, driver_l, motors, odometry, math.radians(90))
    move_straight_for(driver_r, driver_l, motors, odometry, 0.2, 30)
