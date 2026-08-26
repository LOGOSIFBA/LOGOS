from openrdk import CommsRuntime
from openrdk import Motors
from odometry import Odometry
from pid import PID
from line_functions import (
    set_robot_context,
    both_drivers_set_speed,
    both_drivers_stop,
    is_curve_90_candidate,
    centralize_on_line,
    is_gap,
    is_green,
    is_obstacle,
    handle_curve_candidate,
    handle_lost_line,
    handle_obstacle,
    try_cross_gap,
    update_odometry_motors,
    follow_line,
)
from CommandDriver import LatestCommandDriver
import time

base_speed = 25.0
last_position = 0.0
state = "LINE_FOLLOWING"

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

motors = Motors(right=motor_r, left=motor_l)

color_sensor_r = runtime.color_sensor("7C:4F:AD:79:94:B0")
color_sensor_l = runtime.color_sensor("24:EC:4A:CB:05:90")

distance_sensor = runtime.distance_sensor("7C:4F:AD:79:B0:44")

driver_r = LatestCommandDriver(motor_r)
driver_l = LatestCommandDriver(motor_l)

pid = PID()
odometry = Odometry()

set_robot_context(driver_r, driver_l, motors, odometry)

try:
    while True:
        if state == "LINE_FOLLOWING":
            reading = line_sensor.get_data()
            digital = reading["digital"]

            if any(digital):
                last_position = reading["position"]
                
            color_r = color_sensor_r.get_color()
            color_l = color_sensor_l.get_color()

            if color_r == "silver" and color_l == "silver":
                print("Silver detected, entering rescue room state", flush=True)
                state = "RESCUE_ROOM"
                both_drivers_stop()
                continue

            if color_r == "red" and color_l == "red":
                print("Vermelho detectado, parando...", flush=True)
                both_drivers_stop()
                break

     #   if is_obstacle(distance_sensor):
      #      print("Obstacle detected", flush=True)
        #    handle_obstacle(line_sensor)
       #     print("-------------------------------------------------\n", flush=True)
         #   continue


            if is_curve_90_candidate(digital):
                print("90 Curve candidate detected", flush=True)
                handle_curve_candidate(line_sensor, color_sensor_r, color_sensor_l)
                print("-------------------------------------------------\n", flush=True)
                continue


            if is_gap(digital):
                print("Gap detected", flush=True)
                gap_found = try_cross_gap(line_sensor)

                if not gap_found:
                    print("Gap not found, handling lost line", flush=True)
                    handle_lost_line(line_sensor, last_position)

                continue

            follow_line(reading, pid, base_speed)
            print("-------------------------------------------------\n", flush=True)

        if state == "RESCUE_ROOM":
            print("Rescue room state", flush=True)

        if state == "EXIT_RESCUE_ROOM":    
            print("Exit rescue room state", flush=True)

            reading = line_sensor.get_data()
            digital = reading["digital"]

            if any(digital):
                print("Line detected, returning to follow line state", flush=True)
                state = "FOLLOW_LINE"
                continue

except KeyboardInterrupt:
    print("Encerrando...", flush=True)

finally:
    driver_r.shutdown()
    driver_l.shutdown()
