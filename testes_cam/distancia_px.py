"""
Medição de distância em tempo real usando a câmera calibrada.

D = (W_real * fx) / w_pixels

onde:
 W_real   = largura real do objeto (cm) -> ajuste conforme o objeto usado
 fx       = distância focal calibrada (px) -> já calibrado para esta C270
 w_pixels = largura do objeto detectado na imagem (px)

Pressione 'q' para sair.
"""

import cv2

# ---------- CONFIGURAÇÕES ----------
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
THRESH_VALUE = 50
MIN_AREA = 500

FX = 1547.0        # fx calibrado (px) - resultado da calibração feita com a C270
W_REAL_CM = 12.6     # largura real do objeto que será medido (cm) - AJUSTE conforme o objeto
# ------------------------------------

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    print("Erro: não foi possível abrir a câmera.")
    exit()

print("Pressione 'q' para sair")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, THRESH_VALUE, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        maior_contorno = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(maior_contorno)

        if area > MIN_AREA:
            x, y, w, h = cv2.boundingRect(maior_contorno)

            # Calcula a distância usando a largura detectada
            distancia_cm = (W_REAL_CM * FX) / w

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            texto_px = f"w={w}px  h={h}px"
            texto_dist = f"Distancia: {distancia_cm:.1f} cm"

            cv2.putText(frame, texto_px, (x, y - 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, texto_dist, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

    cv2.imshow("Camera", frame)
    cv2.imshow("Threshold", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()