import time
import cv2
import numpy as np

# ---------- CONFIGURAÇÕES DE CALIBRAÇÃO ----------
CAMERA_INDEX = 1
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Cole aqui o fx médio gerado pelo script de calibração (executado em 1280x720)
FX = 1230.29
FY = FX  # Para pixels quadrados

DIAMETRO_REAL_CM = 5  # Diâmetro real da esfera em cm

# Centro óptico (CX0, CY0) - inicializado no centro do frame
CX0 = FRAME_WIDTH / 2.0
CY0 = FRAME_HEIGHT / 2.0

# ---------- PARÂMETROS OPTIMIZADOS (PERTO + LONGE) ----------
DP = 1.2
MIN_DIST = 50        # Reduzido para aceitar bolas grandes/próximas
PARAM1 = 90          # Canny High Threshold base
PARAM2 = 38          # Reduzido de 50 para 38 (detecta muito melhor de perto)
MIN_RADIUS = 10      # Permite detectar esferas mais distantes
MAX_RADIUS = 0       # 0 = Sem limite superior (permite esferas ocupando a tela toda)
# -----------------------------------------------------------


def preprocessar_para_hough(gray_frame):
    """Tratamento de imagem com remoção de brilho e CLAHE para contraste dinâmico."""
    _, mascara_brilho = cv2.threshold(gray_frame, 235, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mascara_brilho = cv2.dilate(mascara_brilho, kernel, iterations=1)

    if cv2.countNonZero(mascara_brilho) > 0:
        sem_brilho = cv2.inpaint(gray_frame, mascara_brilho, 3, cv2.INPAINT_TELEA)
    else:
        sem_brilho = gray_frame

    normalizado = cv2.normalize(sem_brilho, None, 0, 255, cv2.NORM_MINMAX)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    equalizado = clahe.apply(normalizado)
    blur = cv2.medianBlur(equalizado, 5)

    return blur


def calcular_canny_automatico(imagem, sigma=0.33, minimo=40):
    mediana = np.median(imagem)
    upper = int(min(255, (1.0 + sigma) * mediana))
    return max(upper, minimo)


def calcular_posicao_3d(cx, cy, diametro_px):
    if diametro_px <= 0:
        return None
    z = (DIAMETRO_REAL_CM * FX) / diametro_px
    x = (cx - CX0) * z / FX
    y = (cy - CY0) * z / FY
    return np.array([x, y, z], dtype=float)


# Inicialização da Câmera
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

print("Aguardando estabilização da câmera...")
time.sleep(2)
print("Sistema pronto. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = preprocessar_para_hough(gray)
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
        circles_ordenados = sorted(circles, key=lambda c: c[2], reverse=True)

        alvo = circles_ordenados[0]
        segunda = circles_ordenados[1] if len(circles_ordenados) >= 2 else None

        # --- Bola Alvo (Maior) ---
        cx_a, cy_a, r_a = alvo
        pos_a = calcular_posicao_3d(cx_a, cy_a, r_a * 2)

        if pos_a is not None:
            dist_a = pos_a[2]
            cv2.circle(frame, (cx_a, cy_a), r_a, (0, 255, 0), 2)
            cv2.circle(frame, (cx_a, cy_a), 3, (0, 0, 255), -1)
            cv2.putText(frame, "ALVO", (cx_a - r_a, cy_a - r_a - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Dist: {dist_a:.1f} cm", (cx_a - r_a, cy_a - r_a - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        # --- Bola Referência (Segunda Maior) ---
        if segunda is not None:
            cx_b, cy_b, r_b = segunda
            pos_b = calcular_posicao_3d(cx_b, cy_b, r_b * 2)

            if pos_b is not None:
                dist_b = pos_b[2]
                cv2.circle(frame, (cx_b, cy_b), r_b, (255, 150, 0), 2)
                cv2.circle(frame, (cx_b, cy_b), 3, (0, 0, 255), -1)
                cv2.putText(frame, f"Dist: {dist_b:.1f} cm", (cx_b - r_b, cy_b - r_b - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 150, 0), 2)

                # --- Distância 3D entre as esferas ---
                if pos_a is not None:
                    dist_3d = np.linalg.norm(pos_a - pos_b)
                    cv2.line(frame, (cx_a, cy_a), (cx_b, cy_b), (0, 255, 255), 2)
                    mx, my = (cx_a + cx_b) // 2, (cy_a + cy_b) // 2
                    cv2.putText(frame, f"Entre bolas: {dist_3d:.1f} cm", (mx - 60, my - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow("Deteccao e Distancia 3D", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()