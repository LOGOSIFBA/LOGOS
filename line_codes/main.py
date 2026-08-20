from openrdk import CommsRuntime
from openrdk import Motors
from Odometry import Odometry
from pid import PID
from line_functions import (
    is_clear_intersection,
    is_left_90_candidate,
    is_right_90_candidate,
    is_gap,
    is_green,
    is_obstacle,
    detect_color_marking,
    handle_color_marking,
    handle_left_candidate,
    handle_right_candidate,
    handle_color_90_left,
    handle_color_90_right,
    handle_180,
    handle_intersection,
    handle_lost_line,
    handle_obstacle,
    try_cross_gap,
    update_odometry_motors,
    follow_line,
)
from CommandDriver import LatestCommandDriver
import time

base_speed = 20.0

runtime = CommsRuntime(
    auto_start=True,
    enable_webview=True,
    enable_webview_updates=False,
)
print("Runtime OK, conectando motor_r...", flush=True)

motor_r = runtime.traction("98:3D:AE:43:50:50")
print("motor_r OK, conectando motor_l...", flush=True)
motor_l = runtime.traction("10:20:BA:AA:E7:28")
print("motor_l OK, conectando line_sensor...", flush=True)

line_sensor = runtime.line_sensor("10:20:BA:AC:F4:B0")
print("line_sensor OK, entrando no loop...", flush=True)
motors = Motors(right = motor_r, left = motor_l)

color_sensor_r = runtime.color_sensor("7C:4F:AD:79:94:B0")
color_sensor_l = runtime.color_sensor("24:EC:4A:CB:05:90")

distance_sensor = runtime.distance_sensor("7C:4F:AD:79:B0:44")

driver_r = LatestCommandDriver(motor_r)
driver_l = LatestCommandDriver(motor_l)

pid = PID()
odometry = Odometry()
try:
    while True:
        reading = line_sensor.get_data()
        digital = reading["digital"]
        color_r = color_sensor_r.get_color() 
        color_l = color_sensor_l.get_color()

        if is_green(color_r) or is_green(color_l):
            print("Green detected", flush=True)
            color_marking = detect_color_marking(driver_r, driver_l, color_sensor_r, color_sensor_l)
        else:
            color_marking = None
        
        if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
            print("-------------------------------------------------\n", flush=True)
            continue
        
        if is_obstacle(distance_sensor):
            handle_obstacle(driver_r, driver_l, motors, odometry, line_sensor)
            print("-------------------------------------------------\n", flush=True)
            continue

        if is_clear_intersection(digital):
            print("Intersection detected", flush=True)

            color_marking = detect_color_marking(driver_r, driver_l, color_sensor_r, color_sensor_l)

            if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
                print("Color marking handled after intersection", flush=True)
                print("-------------------------------------------------\n", flush=True)
                continue
            
            print("Handling intersection", flush=True)
            print("-------------------------------------------------\n", flush=True)
            driver_r.set_speed(20)
            driver_l.set_speed(20)
            time.sleep(0.3)
            continue

        
        if is_left_90_candidate(digital):
            print("Left 90 candidate detected", flush=True)

            driver_r.stop()
            driver_l.stop()
            color_marking = detect_color_marking(driver_r, driver_l, color_sensor_r, color_sensor_l)

            if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
                print("Color marking handled after intersection", flush=True)
                print("-------------------------------------------------\n", flush=True)
                continue

            handle_left_candidate(driver_r, driver_l, motors, line_sensor, odometry)
            print("-------------------------------------------------\n", flush=True)
            continue

        if is_right_90_candidate(digital):
            print("Right 90 candidate detected", flush=True)

            color_marking = detect_color_marking(driver_r, driver_l, color_sensor_r, color_sensor_l)

            if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
                print("Color marking handled after intersection", flush=True)
                print("-------------------------------------------------\n", flush=True)
                continue

            handle_right_candidate(driver_r, driver_l, motors, line_sensor, odometry)
            print("-------------------------------------------------\n", flush=True)
            continue
            
        if color_r == "red" and color_l == "red":
            print("Vermelho detectado, parando...", flush=True)
            driver_r.stop()
            driver_l.stop()
            break
        
        follow_line(driver_r, driver_l, reading, pid, base_speed)
        print("-------------------------------------------------\n", flush=True)

except KeyboardInterrupt:
    print("Encerrando...", flush=True)
finally:
    driver_r.stop()
    driver_l.stop()
