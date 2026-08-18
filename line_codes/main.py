from openrdk import CommsRuntime
from openrdk import Motors
from odometry import Odometry
from pid import PID
from CommandDriver import LatestCommandDriver
from line_functions import (
    is_clear_intersection,
    is_left_90_candidate,
    is_right_90_candidate,
    is_gap,
    is_green,
    is_obstacle,
    detect_color_marking,
    handle_left_candidate,
    handle_right_candidate,
    handle_color_90_left,
    handle_color_90_right,
    handle_180,
    handle_color_marking,
    handle_intersection,
    handle_lost_line,
    handle_obstacle,
    move_straight_for,
    try_cross_gap,
    update_odometry_motors,
    follow_line,
)
import time

BASE_SPEED = 15.0
last_position = 0.0

runtime = CommsRuntime(
    auto_start=True,
    enable_webview=True,
    enable_webview_updates=True,
)

motor_r = runtime.traction("98:3D:AE:43:50:50")
motor_l = runtime.traction("10:20:BA:AA:E7:28")
line_sensor = runtime.line_sensor("10:20:BA:AC:F4:B0")
distance_sensor = runtime.distance_sensor("7C:4F:AD:79:B0:44")
color_sensor_r = runtime.color_sensor("7C:4F:AD:79:94:B0")
color_sensor_l = runtime.color_sensor("Serial_Number")

motors = Motors(right=motor_r, left=motor_l)

driver_r = LatestCommandDriver(motor_r)
driver_l = LatestCommandDriver(motor_l)

pid = PID()
odometry = Odometry()

try:
    while True:
        reading = line_sensor.get_data()
        digital = reading["digital"]
        update_odometry_motors(odometry, motors)
        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r) or is_green(color_l):
            color_marking = detect_color_marking(color_sensor_r, color_sensor_l)
        else:
            color_marking = None

        if reading["line_detected"]:
            last_position = reading["position"]

        if is_obstacle(distance_sensor):
            handle_obstacle(driver_r, driver_l, motors, odometry)
            continue

        if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
            continue

        if is_clear_intersection(digital):
            move_straight_for(driver_r, driver_l, motors, odometry, 0.15, 30)

            if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
                continue

            handle_intersection(driver_r, driver_l, motors, odometry)
            continue

        if is_left_90_candidate(digital):
            handle_left_candidate(driver_r, driver_l, motors, line_sensor, odometry)
            continue

        if is_right_90_candidate(digital):
            handle_right_candidate(driver_r, driver_l, motors, line_sensor, odometry)
            continue

        if is_gap(reading):
            gap_found = try_cross_gap(driver_r, driver_l, motors, line_sensor, odometry)

            if not gap_found:
                handle_lost_line(driver_r, driver_l, motors, line_sensor, last_position, odometry)

            continue

        follow_line(driver_r, driver_l, reading, pid, BASE_SPEED)

finally:
    driver_r.stop()
    driver_l.stop()
