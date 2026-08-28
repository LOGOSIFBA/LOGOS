import cv2
import numpy as np


def nada(x):
    pass


CAMERA_INDEX = 1

# Janela para controle dos sliders (Trackbars)
cv2.namedWindow("Calibracao HSV")
cv2.resizeWindow("Calibracao HSV", 640, 300)

# Sliders para os limites de H (0-179), S (0-255) e V (0-255)
cv2.createTrackbar("H Min", "Calibracao HSV", 0, 179, nada)
cv2.createTrackbar("H Max", "Calibracao HSV", 179, 179, nada)
cv2.createTrackbar("S Min", "Calibracao HSV", 0, 255, nada)
cv2.createTrackbar("S Max", "Calibracao HSV", 255, 255, nada)
cv2.createTrackbar("V Min", "Calibracao HSV", 0, 255, nada)
cv2.createTrackbar("V Max", "Calibracao HSV", 255, 255, nada)

cap = cv2.VideoCapture(CAMERA_INDEX)

# Desativa ajustes automáticos para evitar variação na calibração
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_AUTO_WB, 0)

print("Instruções:")
print(" - Pressione 'c' para imprimir os valores HSV formatados no terminal.")
print(" - Pressione 'q' para fechar o programa.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Leitura em tempo real dos sliders
    h_min = cv2.getTrackbarPos("H Min", "Calibracao HSV")
    h_max = cv2.getTrackbarPos("H Max", "Calibracao HSV")
    s_min = cv2.getTrackbarPos("S Min", "Calibracao HSV")
    s_max = cv2.getTrackbarPos("S Max", "Calibracao HSV")
    v_min = cv2.getTrackbarPos("V Min", "Calibracao HSV")
    v_max = cv2.getTrackbarPos("V Max", "Calibracao HSV")

    limite_baixo = np.array([h_min, s_min, v_min])
    limite_alto = np.array([h_max, s_max, v_max])

    # Criação da máscara e aplicação no frame original
    mascara = cv2.inRange(hsv, limite_baixo, limite_alto)
    resultado = cv2.bitwise_and(frame, frame, mask=mascara)

    cv2.imshow("Original", frame)
    cv2.imshow("Mascara", mascara)
    cv2.imshow("Resultado", resultado)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("c"):
        print("\n--- VALORES HSV CALIBRADOS ---")
        print(f"VERDE_BAIXO = np.array([{h_min}, {s_min}, {v_min}])")
        print(f"VERDE_ALTO  = np.array([{h_max}, {s_max}, {v_max}])")

cap.release()
cv2.destroyAllWindows()