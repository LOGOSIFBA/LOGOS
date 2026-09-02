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