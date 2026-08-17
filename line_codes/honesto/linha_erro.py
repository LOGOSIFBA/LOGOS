import cv2
import numpy as np
import time

# =========================
# CÂMERA
# =========================

index = 1
camera = cv2.VideoCapture(index)

if not camera.isOpened():
    print("Não abriu a câmera.")
    exit()

# Como a câmera está funcionando em 640x480:
centro = 640 / 2


# =========================
# PID
# =========================

class PID:
    def __init__(self):
        self.kp = 1
        self.ki = 0
        self.kd = 0
        self.last_error = None
        self.integral = 0
        self.last_time = None
        self.set_point = 0

    def calculate(self, position):
        now = time.monotonic()
        error = self.set_point - position

        if self.last_time is None or self.last_error is None:
            derivative = 0
        else:
            dt = now - self.last_time

            if dt > 0.15 or dt <= 0:
                derivative = 0
            else:
                derivative = (error - self.last_error) / dt
                self.integral += error * dt

        result = (
            self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )

        result = max(-100, min(100, result))

        self.last_time = now
        self.last_error = error

        return result


pid = PID()


# =========================
# LOOP PRINCIPAL
# =========================

while True:

    ret, frame = camera.read()

    if not ret:
        print("Erro ao ler câmera")
        break

    # ROI usada no seu código original
    frameroi = frame[281:480, 1:640]

    # Converte para escala de cinza
    imgcinza = cv2.cvtColor(frameroi, cv2.COLOR_BGR2GRAY)

    # Limiarização
    ret, img = cv2.threshold(
        imgcinza,
        130,
        255,
        cv2.THRESH_BINARY
    )

    # Pega a linha inferior da ROI
    linha = img[198, :]

    # Encontra os pixels pretos
    x = np.where(linha == 0)

    if len(x[0]) > 0:

        # Posição média dos pixels pretos
        position = np.mean(x[0])

        # Posição em relação ao centro
        posicao_relativa = position - centro

        # PID
        result = pid.calculate(posicao_relativa)

        print(
            f"posição: {position:.2f} | "
            f"erro: {posicao_relativa:.2f} | "
            f"PID: {result:.2f}"
        )

    else:
        print("Nenhum pixel preto encontrado.")

    # Mostra a imagem original
    cv2.imshow("Logitech", frame)

    # Mostra a imagem limiarizada
    cv2.imshow("Lindezas limiarizadas", img)

    # Q para sair
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()

----

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

base_speed = 15.0

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

driver_r = LatestCommandDriver(motor_r)
driver_l = LatestCommandDriver(motor_l)

pid = PID()
odometry = Odometry()
try:
    while True:
        reading = line_sensor.get_data()
        color_r = color_sensor_r.get_color() 
        color_l = color_sensor_l.get_color()

        if is_green(color_r) or is_green(color_l):
            color_marking = detect_color_marking(color_sensor_r, color_sensor_l)
        else:
            color_marking = None
        
        if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
            continue

        if is_clear_intersection(digital):
            driver_l.set_speed(15)
            driver_r.set_speed(15)
            time.sleep(0.2)
        
            if handle_color_marking(color_marking, driver_r, driver_l, motors, odometry):
                continue
            else:
                driver_r.set_speed(20)
                driver_l.set_speed(20)
                time.sleep(0.4)
                continue

        if is_left_90_candidate(digital):
            handle_left_candidate(driver_r, driver_l, motors, line_sensor, odometry)
            continue

        if is_right_90_candidate(digital):
            handle_right_candidate(driver_r, driver_l, motors, line_sensor, odometry)
            continue
        
        
        if color_r == "red" and color_l == "red":
            driver_r.stop()
            driver_l.stop()
            break
        
        follow_line(driver_r, driver_l, reading, pid, BASE_SPEED)

finally:
    driver_r.stop()
    driver_l.stop()
