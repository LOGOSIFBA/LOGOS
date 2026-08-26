import time
import math

driver_r = None
driver_l = None
motors = None
odometry = None
last_line_time = time.monotonic()


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


def is_curve_90_candidate(digital):
    return (
    (digital[0] and digital[1] and  digital[2] and not digital[3] and not digital[4]) #Left
    or 
    (digital[3] and digital[4] and digital[2] and not digital[0] and not digital[1]) #Right
    or
    (all(digital))
    )


def is_green(color):
    return color == "green"


def is_red(color):
    return color == "red"


def detect_color_marking(color_sensor_r, color_sensor_l):
    print("Detecting color marking", flush=True)

    right_green_count = 0
    left_green_count = 0

    both_drivers_set_speed(10, 10)

    right_time = 0.45
    left_time = right_time * 2

    start_time = time.monotonic()

    while time.monotonic() - start_time < 0.3:
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

    both_drivers_set_speed(-15, -15)
    time.sleep(0.2)
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



def is_gap(digital):
    global last_line_time

    if any(digital):
        last_line_time = time.monotonic()
        return False

    return time.monotonic() - last_line_time >= 0.2


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
    both_drivers_set_speed(speed, speed)
    time.sleep(duration)

    both_drivers_stop()


def handle_intersection():
    move_straight_for(0.3, 20)

def ways_check(line_sensor):
    right = False
    left = False
    front = False
    ways = 0
    right_curve = 1.55
    left_curve = right_curve * 2

    centralize_on_line(line_sensor)

    move_straight_for(0.85, 20)

    reading = line_sensor.get_data()
    digital = reading["digital"]

    if any(digital):
        front = True
        ways += 1

    print(front, flush=True)

    both_drivers_set_speed(30, -30)
    time.sleep(right_curve)

    reading = line_sensor.get_data()
    digital = reading["digital"]

    if any(digital):
        right = True
        ways += 1

    print(right, flush=True)

    both_drivers_set_speed(-30, 30)
    time.sleep(left_curve)

    reading = line_sensor.get_data()
    digital = reading["digital"]

    if any(digital):
        left = True
        ways += 1

    print(left, flush=True)

    if ways != 1:
        both_drivers_set_speed(30, -30)
        time.sleep(right_curve)
        centralize_on_line(line_sensor)
        move_straight_for(0.25, 30)
        print("Green check is necessary", flush=True)
        return True
    elif front:
        both_drivers_set_speed(30, -30)
        time.sleep(right_curve)
        centralize_on_line(line_sensor)
    elif left:
        centralize_on_line(line_sensor)
    elif right:
        both_drivers_set_speed(30, -30)
        time.sleep(right_curve*2)
        centralize_on_line(line_sensor)


def handle_curve_candidate(line_sensor, color_sensor_r, color_sensor_l):
    print("Handling curve candidate", flush=True)
    needs_green_check = ways_check(line_sensor)

    if needs_green_check:
        color_marking = detect_color_marking(color_sensor_r, color_sensor_l)

        handle_color_marking(color_marking)


def handle_color_marking(color_marking):
    if color_marking == "180":
        print("Color 180 detected", flush=True)
        both_drivers_set_speed(30, -30)
        time.sleep(4.4)
        return True

    if color_marking == "LEFT":
        print("Color 90 left detected", flush=True)
        both_drivers_set_speed(20, 20)
        time.sleep(1.0)
        both_drivers_set_speed(30, -30)
        time.sleep(1.8)
        return True

    if color_marking == "RIGHT":
        print("Color 90 right detected", flush=True)
        both_drivers_set_speed(20, 20)
        time.sleep(1.0)
        both_drivers_set_speed(-30, 30)
        time.sleep(1.8)
        return True

    return False


def follow_line(reading, pid, base_speed):
    print("Following line", flush=True)
    position = reading["position"]

    correction = pid.calculate(position)

    print(pid.get_pid())
    left_speed = base_speed + correction
    right_speed = base_speed - correction

    left_speed = max(-60.0, min(60.0, left_speed))
    right_speed = max(-60.0, min(60.0, right_speed))

    both_drivers_set_speed(left_speed, right_speed)


def try_cross_gap(line_sensor):
    print("Trying to cross gap", flush=True)
    start_time = time.monotonic()

    both_drivers_set_speed(30, 30)
    while time.monotonic() - start_time < 2.0:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if any(digital):
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

    if last_position > 0:
        left_speed = -30
        right_speed = 30
    else:
        left_speed = 30
        right_speed = -30

    both_drivers_set_speed(left_speed, right_speed)

    while True:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
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

def centralize_on_line(line_sensor):
    move_straight_for(0.6, -20)
    time.sleep(0.1)

    both_drivers_set_speed(-30, 30)

    start_time = time.monotonic()
    right_turn_time = 0.4

    while time.monotonic() - start_time < right_turn_time:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            time.sleep(0.1)
            move_straight_for(0.3, 20)
            return True

    left_turn_time = right_turn_time * 2

    both_drivers_set_speed(30, -30)

    start_time = time.monotonic()

    while time.monotonic() - start_time < left_turn_time:
        reading = line_sensor.get_data()
        digital = reading["digital"]

        if digital[2]:
            both_drivers_stop()
            time.sleep(0.1)
            move_straight_for(0.3, 20)
            return True

    both_drivers_set_speed(-30, 30)

    time.sleep(right_turn_time)

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
