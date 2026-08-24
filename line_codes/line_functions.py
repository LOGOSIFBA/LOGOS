import time
import math

driver_r = None
driver_l = None
motors = None
odometry = None


def set_robot_context(right_driver, left_driver, robot_motors, robot_odometry):
    global driver_r, driver_l, motors, odometry

    driver_r = right_driver
    driver_l = left_driver
    motors = robot_motors
    odometry = robot_odometry


def both_drivers_set_speed(left_speed, right_speed):
    driver_l.set_speed(left_speed)
    driver_r.set_speed(right_speed)


def both_drivers_stop():
    driver_r.stop()
    driver_l.stop()


def is_clear_intersection(digital):
    return all(digital)


def is_left_90_candidate(digital):
    return digital[0] and digital[1] and not digital[3] and not digital[4]


def is_green(color):
    return color == "green"


def is_red(color):
    return color == "red"


def detect_color_marking(color_sensor_r, color_sensor_l):
    print("Detecting color marking", flush=True)

    right_green_count = 0
    left_green_count = 0

    both_drivers_set_speed(10, 10)

    right_time = 0.3
    left_time = right_time * 2

    start_time = time.monotonic()

    while time.monotonic() - start_time < 0.2:
        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r):
            right_green_count += 1

        if is_green(color_l):
            left_green_count += 1

    both_drivers_set_speed(-15, 15)

    start_time = time.monotonic()

    while time.monotonic() - start_time < right_time:
        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r):
            right_green_count += 1

        if is_green(color_l):
            left_green_count += 1

    both_drivers_set_speed(15, -15)

    start_time = time.monotonic()

    while time.monotonic() - start_time < left_time:
        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r):
            right_green_count += 1

        if is_green(color_l):
            left_green_count += 1

    both_drivers_set_speed(-15, 15)

    start_time = time.monotonic()

    while time.monotonic() - start_time < right_time:
        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r):
            right_green_count += 1

        if is_green(color_l):
            left_green_count += 1

    both_drivers_stop()

    print(f"Right green count: {right_green_count}, Left green count: {left_green_count}", flush=True)

    right_confirmed = right_green_count >= 2
    left_confirmed = left_green_count >= 2

    if right_confirmed and left_confirmed:
        return "180"

    if right_confirmed and not left_confirmed:
        return "RIGHT"

    if left_confirmed and not right_confirmed:
        return "LEFT"

    return None


def is_right_90_candidate(digital):
    return digital[3] and digital[4] and not digital[0] and not digital[1]


def is_gap(reading):
    return not reading["line_detected"]


def update_odometry_motors():
    right_data = motors.right.get_position_telemetry()
    left_data = motors.left.get_position_telemetry()

    right_deg = right_data["position_deg"]
    left_deg = left_data["position_deg"]

    odometry.update(right_deg, left_deg)


def turn_left(target_angle_rad):
    update_odometry_motors()
    start_theta = odometry.theta

    while True:
        both_drivers_set_speed(30, -30)

        update_odometry_motors()

        turned_angle = odometry.angle_difference_rad(odometry.theta, start_theta)

        if turned_angle >= target_angle_rad:
            break

    both_drivers_stop()


def turn_right(target_angle_rad):
    update_odometry_motors()
    start_theta = odometry.theta

    while True:
        both_drivers_set_speed(-30, 30)

        update_odometry_motors()

        turned_angle = odometry.angle_difference_rad(odometry.theta, start_theta)

        if turned_angle <= -target_angle_rad:
            break

    both_drivers_stop()


def move_straight_for(duration, speed):
    start_time = time.monotonic()

    while time.monotonic() - start_time < duration:
        both_drivers_set_speed(speed, speed)

        update_odometry_motors()

    both_drivers_stop()


def center_stays_on_line_during_short_forward(line_sensor):
    both_drivers_set_speed(30, 30)

    start_time = time.monotonic()

    while time.monotonic() - start_time < 0.25:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            return True

    right_turn_time = 1.2

    both_drivers_set_speed(-30, 30)

    start_time = time.monotonic()

    while time.monotonic() - start_time < right_turn_time:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            return True

    left_turn_time = right_turn_time * 2

    both_drivers_set_speed(30, -30)

    start_time = time.monotonic()

    while time.monotonic() - start_time < left_turn_time:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            return True

    both_drivers_set_speed(-30, 30)

    time.sleep(right_turn_time)

    both_drivers_stop()

    return False


def handle_intersection():
    move_straight_for(0.3, 20)


def handle_left_candidate(line_sensor):
    print("Handling left candidate", flush=True)
    center_stayed = center_stays_on_line_during_short_forward(line_sensor)

    if center_stayed:
        print("Center stayed on line during short forward", flush=True)
        both_drivers_set_speed(30, 30)
        time.sleep(0.35)
    else:
        print("Center did not stay on line, turning left", flush=True)
        both_drivers_set_speed(30, -30)
        time.sleep(1.6)


def handle_right_candidate(line_sensor):
    print("Handling right candidate", flush=True)
    center_stayed = center_stays_on_line_during_short_forward(line_sensor)

    if center_stayed:
        print("Center stayed on line during short forward", flush=True)
        both_drivers_set_speed(30, 30)
        time.sleep(0.35)
    else:
        print("Center did not stay on line, turning right", flush=True)
        both_drivers_set_speed(-30, 30)
        time.sleep(1.6)


def handle_color_marking(color_marking):
    if color_marking == "180":
        print("Color 180 detected", flush=True)
        both_drivers_set_speed(30, -30)
        time.sleep(4.4)
        return True

    if color_marking == "LEFT":
        print("Color 90 left detected", flush=True)
        both_drivers_set_speed(30, -30)
        time.sleep(1.8)
        both_drivers_set_speed(20, 20)
        time.sleep(1.2)
        return True

    if color_marking == "RIGHT":
        print("Color 90 right detected", flush=True)
        both_drivers_set_speed(-30, 30)
        time.sleep(1.8)
        both_drivers_set_speed(20, 20)
        time.sleep(1.2)
        return True

    return False


def follow_line(reading, pid, base_speed):
    print("Following line", flush=True)
    position = reading["position"]

    correction = pid.calculate(position)

    left_speed = base_speed + correction
    right_speed = base_speed - correction

    left_speed = max(-50.0, min(50.0, left_speed))
    right_speed = max(-50.0, min(50.0, right_speed))

    both_drivers_set_speed(left_speed, right_speed)


def try_cross_gap(line_sensor):
    start_time = time.monotonic()

    while time.monotonic() - start_time < 3.0:
        both_drivers_set_speed(30, 30)

        update_odometry_motors()

        reading = line_sensor.get_data()

        if reading["line_detected"]:
            both_drivers_stop()
            return True

    forward_time = time.monotonic() - start_time

    move_straight_for(forward_time, -30)
    return False


def is_obstacle(distance_sensor):
    distance = distance_sensor.get_distance_cm()

    if distance is None:
        return False

    return distance < 4


def handle_lost_line(line_sensor, last_position):
    center_count = 0

    if last_position < 0:
        left_speed = 15
        right_speed = 30
    else:
        left_speed = 30
        right_speed = 15

    while True:
        both_drivers_set_speed(left_speed, right_speed)

        update_odometry_motors()

        reading = line_sensor.get_data()
        digital = reading["digital"]

        if reading["line_detected"] and digital[2]:
            center_count += 1
        else:
            center_count = 0

        if center_count >= 3:
            both_drivers_stop()
            return True


def handle_obstacle(line_sensor):
    print("Handling obstacle", flush=True)
    both_drivers_stop()

    time.sleep(0.2)

    # Andar pra trás
    both_drivers_set_speed(-20, -20)
    time.sleep(0.2)

    # Vira pra direita
    both_drivers_set_speed(-30, 30)
    time.sleep(2.1)

    # Anda pra frente
    both_drivers_set_speed(30, 30)
    time.sleep(1.7)

    # Vira pra esquerda
    both_drivers_set_speed(30, -30)
    time.sleep(2.1)

    # Anda pra frente pra passar obstaculo
    both_drivers_set_speed(30, 30)
    time.sleep(3.3)

    # Vira pra esquerda
    both_drivers_set_speed(30, -30)
    time.sleep(2.3)

    # Anda pra frente
    both_drivers_set_speed(30, 30)
    time.sleep(1.7)

    # Vira pra direita
    both_drivers_set_speed(-30, 30)
    time.sleep(2.1)

    reading = line_sensor.get_data()
    digital = reading["digital"]

    if any(digital):
        return True

    both_drivers_set_speed(-30, 30)

    start_time = time.monotonic()

    while time.monotonic() - start_time < 2.8:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            return True

    both_drivers_set_speed(30, -30)

    start_time = time.monotonic()

    while time.monotonic() - start_time < 4.9:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            return True

    both_drivers_stop()

    return False


def handle_180():
    both_drivers_stop()
    turn_right(math.radians(180))


def handle_color_90_left():
    both_drivers_stop()
    turn_left(math.radians(90))
    move_straight_for(0.2, 30)


def handle_color_90_right():
    both_drivers_stop()
    turn_right(math.radians(90))
    move_straight_for(0.2, 30)
