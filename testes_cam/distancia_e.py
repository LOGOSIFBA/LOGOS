"""
Deteccao de esferas + calculo de distancia usando Hough Circle Transform.

D = (Diametro_real * fx) / diametro_pixels

Pressione 'q' para sair.
"""

import cv2
import numpy as np

# ---------- CONFIGURACOES ----------
CAMERA_INDEX = 1

FX = 1347.20      # fx calibrado (px) - o mesmo da calibracao anterior
DIAMETRO_REAL_CM = 4.865  # diametro real da esfera (cm) - AJUSTE conforme a esfera usada

# Parametros do HoughCircles (ajuste conforme necessario)
DP = 1.2                # resolucao inversa do acumulador
MIN_DIST = 100           # distancia minima entre centros de circulos detectados (px)
PARAM1 = 90             # limiar superior do Canny (deteccao de bordas)
PARAM2 = 50             # limiar do acumulador (menor = mais circulos falsos positivos)
MIN_RADIUS = 20          # raio minimo detectavel (px)
MAX_RADIUS = 400         # raio maximo detectavel (px)
# ------------------------------------

def preprocessar_para_hough(gray_frame):
    """
    Pre-processamento para lidar com dois extremos de objeto:
      - Esferas de aluminio: muito reflexivas, geram brilho especular que
        "estoura" a imagem e quebra o contorno circular.
      - Esferas pretas foscas: baixo contraste, bordas fracas que o Canny
        interno do HoughCircles pode nao conseguir detectar.

    Estrategia:
      1. Detecta e remove (inpaint) o brilho especular, se houver
      2. Normaliza o histograma (estica para 0-255) para aproveitar toda a
         faixa dinamica, essencial para objetos escuros em cenas mal iluminadas
      3. Aplica CLAHE (equalizacao de contraste local), que reforca bordas
         tanto em regioes claras quanto escuras
      4. Suaviza com medianBlur antes do Hough
    """
    # 1) Mascara dos pixels "estourados" (brilho especular) e inpaint
    _, mascara_brilho = cv2.threshold(gray_frame, 235, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mascara_brilho = cv2.dilate(mascara_brilho, kernel, iterations=1)

    if cv2.countNonZero(mascara_brilho) > 0:
        sem_brilho = cv2.inpaint(gray_frame, mascara_brilho, 5, cv2.INPAINT_TELEA)
    else:
        sem_brilho = gray_frame

    # 2) Normaliza o histograma (ajuda muito em esferas pretas/pouco iluminadas)
    normalizado = cv2.normalize(sem_brilho, None, 0, 255, cv2.NORM_MINMAX)

    # 3) CLAHE para equalizar contraste local
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    equalizado = clahe.apply(normalizado)

    # 4) Suaviza antes do Hough
    blur = cv2.medianBlur(equalizado, 5)

    return blur, mascara_brilho


def calcular_canny_automatico(imagem, sigma=0.33, minimo=40):
    """
    Calcula um limiar de Canny (usado como 'param1' do HoughCircles) de forma
    adaptativa, baseado na mediana de intensidade da imagem ja pre-processada.

    Isso e importante porque um param1 fixo que funciona bem para a esfera de
    aluminio (bordas fortes/contraste alto) tende a ser alto demais para a
    esfera preta fosca (bordas fracas/contraste baixo), fazendo o Hough
    simplesmente nao detectar o circulo. Com o limiar dinamico, cada frame
    recebe um valor ajustado ao seu proprio nivel de contraste.
    """
    mediana = np.median(imagem)
    upper = int(min(255, (1.0 + sigma) * mediana))
    return max(upper, minimo)


cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
# Aguarda 3 segundos para estabilização de luz
time.sleep(3)

if not cap.isOpened():
    print("Erro: nao foi possivel abrir a camera.")
    exit()

print("Pressione 'q' para sair")

while True:

    ret, frame = cap.read()
    if not ret:
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
        maxRadius=MAX_RADIUS
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        # Pega o maior circulo detectado (assumindo que e a esfera de interesse)
        maior = max(circles, key=lambda c: c[2])
        cx, cy, r = maior
        diametro_px = r * 2

        distancia_cm = (DIAMETRO_REAL_CM * FX) / diametro_px

        # Desenha o circulo e o centro
        cv2.circle(frame, (cx, cy), r, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

        texto_px = f"diametro={diametro_px}px  raio={r}px"
        texto_dist = f"Distancia: {distancia_cm:.1f} cm"

        cv2.putText(frame, texto_px, (cx - r, cy - r - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, texto_dist, (cx - r, cy - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
