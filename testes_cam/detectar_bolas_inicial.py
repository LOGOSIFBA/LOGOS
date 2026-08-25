"""
Deteccao de esferas + calculo de distancia usando Hough Circle Transform.

D = (Diametro_real * fx) / diametro_pixels

Pressione 'q' para sair.
"""

import time
import cv2
import numpy as np

# ---------- CONFIGURACOES ----------
CAMERA_INDEX = 1

FX = 1326.62      # fx calibrado (px)
DIAMETRO_REAL_CM = 4.72  # diametro real da esfera (cm)

# Parametros do HoughCircles
DP = 1.2
MIN_DIST = 100
PARAM1 = 90
PARAM2 = 50
MIN_RADIUS = 20
MAX_RADIUS = 400
# ------------------------------------


def preprocessar_para_hough(gray_frame):
    _, mascara_brilho = cv2.threshold(gray_frame, 235, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mascara_brilho = cv2.dilate(mascara_brilho, kernel, iterations=1)

    if cv2.countNonZero(mascara_brilho) > 0:
        sem_brilho = cv2.inpaint(gray_frame, mascara_brilho, 5, cv2.INPAINT_TELEA)
    else:
        sem_brilho = gray_frame

    normalizado = cv2.normalize(sem_brilho, None, 0, 255, cv2.NORM_MINMAX)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    equalizado = clahe.apply(normalizado)
    blur = cv2.medianBlur(equalizado, 5)

    return blur, mascara_brilho


def calcular_canny_automatico(imagem, sigma=0.33, minimo=40):
    mediana = np.median(imagem)
    upper = int(min(255, (1.0 + sigma) * mediana))
    return max(upper, minimo)


# 1. Inicializa a captura
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # troque para cv2.CAP_DSHOW se estiver no Windows

# 2. Configura buffer para evitar acúmulo de frames velhos
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# 3. Valida se a câmera abriu com sucesso
if not cap.isOpened():
    print("Erro: nao foi possivel abrir a camera.")
    exit()

# 4. Lê a resolução real do hardware
FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Câmera iniciada com resolução: {FRAME_WIDTH}x{FRAME_HEIGHT}")

# 5. Tempo de estabilização do ganho/exposição da câmera
print("Aguardando estabilização de luz (3 segundos)...")
time.sleep(3)

print("Pressione 'q' para sair")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Erro ao capturar frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur, mascara_brilho = preprocessar_para_hough(gray)
    param1_dinamico = calcular_canny_automatico(blur, minimo=PARAM1 // 2)

    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=DP,
        minDist=MIN_DIST,
        param1=param1_dinamico,
        param2=PARAM2,
        minRadius=MIN_RADIUS,
        maxRadius=MAX_RADIUS,
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        maior = max(circles, key=lambda c: c[2])
        cx, cy, r = maior
        diametro_px = r * 2

        distancia_cm = (DIAMETRO_REAL_CM * FX) / diametro_px

        cv2.circle(frame, (cx, cy), r, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

        texto_px = f"diametro={diametro_px}px  raio={r}px"
        texto_dist = f"Distancia: {distancia_cm:.1f} cm"

        cv2.putText(
            frame,
            texto_px,
            (cx - r, cy - r - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            texto_dist,
            (cx - r, cy - r - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 200, 255),
            2,
        )

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
