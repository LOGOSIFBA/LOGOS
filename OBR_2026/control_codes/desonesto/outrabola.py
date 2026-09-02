import cv2
import numpy as np

index = 1
camera = cv2.VideoCapture(index)

while True:
    ret, frame = camera.read()

    # Converte para HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Faixa de cor que queremos detectar
    menor = np.array([0, 100, 100])
    maior = np.array([20, 255, 255])

    # Cria uma máscara
    mascara = cv2.inRange(hsv, menor, maior)

    # Procura os contornos
    contornos, _ = cv2.findContours(
        mascara,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contorno in contornos:

        area = cv2.contourArea(contorno)

        # Ignora coisas pequenas
        if area < 500:
            continue

        (x, y), raio = cv2.minEnclosingCircle(contorno)

        centro = (int(x), int(y))
        raio = int(raio)

        # Desenha o círculo encontrado
        cv2.circle(
            frame,
            centro,
            raio,
            (255, 0, 255),
            2
        )

        # Marca o centro
        cv2.circle(
            frame,
            centro,
            5,
            (255, 0, 255),
            -1
        )

    cv2.imshow("Bola", frame)
    cv2.imshow("Mascara", mascara)

    cv2.waitKey(1)

camera.release()
cv2.destroyAllWindows()