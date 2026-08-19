import cv2
import numpy as np
import time

from openrdk import CommsRuntime
from openrdk import Motors
from Odometry import Odometry
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

BASE_SPEED = 15.0
last_position = 0.0


# =========================================================
# VISÃO COMPUTACIONAL
# =========================================================

index = 0
camera = cv2.VideoCapture(index)

if not camera.isOpened():
    print("Não abriu a câmera.")
    raise SystemExit

centro = 640 / 2


# =========================================================
# SENSORES E MOTORES
# =========================================================

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

motors = Motors(
    right=motor_r,
    left=motor_l
)

color_sensor_r = runtime.color_sensor("7C:4F:AD:79:94:B0")
color_sensor_l = runtime.color_sensor("24:EC:4A:CB:05:90")

driver_r = LatestCommandDriver(motor_r)
driver_l = LatestCommandDriver(motor_l)

pid = PID()
odometry = Odometry()


try:

    while True:

        # =================================================
        # SENSORES
        # =================================================

        reading = line_sensor.get_data()
        digital = reading["digital"]

        update_odometry_motors(
            odometry,
            motors
        )

        color_r = color_sensor_r.get_color()
        color_l = color_sensor_l.get_color()

        if is_green(color_r) or is_green(color_l):
            color_marking = detect_color_marking(
                color_sensor_r,
                color_sensor_l
            )
        else:
            color_marking = None

        if reading["line_detected"]:
            last_position = reading["position"]


        # =================================================
        # VISÃO COMPUTACIONAL
        # =================================================

        ret, frame = camera.read()

        if not ret:
            print("Erro ao ler câmera", flush=True)
            continue

        frameroi = frame[281:480, 1:640]

        imgcinza = cv2.cvtColor(
            frameroi,
            cv2.COLOR_BGR2GRAY
        )

        _, img = cv2.threshold(
            imgcinza,
            130,
            255,
            cv2.THRESH_BINARY
        )

        linha = img[198, :]

        x = np.where(linha == 0)

        if len(x[0]) > 0:

            position = np.mean(x[0])

            posicao_relativa = position - centro

            correction = pid.calculate(
                posicao_relativa
            )

            print(
                f"posição: {position:.2f} | "
                f"erro: {posicao_relativa:.2f} | "
                f"PID: {correction:.2f}",
                flush=True
            )

        else:

            position = None
            correction = 0

            print(
                "Nenhum pixel preto encontrado.",
                flush=True
            )


        # =================================================
        # SENSORES
        # =================================================

        if handle_color_marking(
            color_marking,
            driver_r,
            driver_l,
            motors,
            odometry
        ):
            continue

        if is_clear_intersection(digital):

            # -------------------------------------------------
            # ANDAR ORIGINAL DOS MENINOS
            # -------------------------------------------------

            # driver_l.set_speed(15)
            # driver_r.set_speed(15)
            # time.sleep(0.2)

            if handle_color_marking(
                color_marking,
                driver_r,
                driver_l,
                motors,
                odometry
            ):
                continue

            # driver_r.set_speed(20)
            # driver_l.set_speed(20)
            # time.sleep(0.4)

            continue


        if is_left_90_candidate(digital):

            handle_left_candidate(
                driver_r,
                driver_l,
                motors,
                line_sensor,
                odometry
            )

            continue


        if is_right_90_candidate(digital):

            handle_right_candidate(
                driver_r,
                driver_l,
                motors,
                line_sensor,
                odometry
            )

            continue


        if color_r == "red" and color_l == "red":

            driver_r.stop()
            driver_l.stop()

            break


        # =================================================
        # ANDAR
        # =================================================

        if correction is not None:

            left_speed = BASE_SPEED + correction
            right_speed = BASE_SPEED - correction

            left_speed = max(
                -50,
                min(50, left_speed)
            )

            right_speed = max(
                -50,
                min(50, right_speed)
            )

            driver_l.set_speed(left_speed)
            driver_r.set_speed(right_speed)


        # -------------------------------------------------
        # ANDAR ORIGINAL DOS MENINOS
        # -------------------------------------------------

        # follow_line(
        #     driver_r,
        #     driver_l,
        #     reading,
        #     pid,
        #     BASE_SPEED
        # )


        # =================================================
        # VISÃO COMPUTACIONAL
        # =================================================

        cv2.imshow(
            "Logitech",
            frame
        )

        cv2.imshow(
            "Lindezas limiarizadas",
            img
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


finally:

    driver_r.stop()
    driver_l.stop()

    camera.release()
    cv2.destroyAllWindows()
