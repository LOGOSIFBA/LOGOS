"""
Detecção de vermelho e verde usando OpenCV + máscara HSV
----------------------------------------------------------
Requisitos:
    pip install opencv-python numpy

Uso:
    python detecta_cores.py

Pressione "q" para sair.
"""

import cv2
import numpy as np

# --- Faixas de cor em HSV ---
# OBS: no OpenCV, H vai de 0 a 179 (não 0-360)

# Verde: geralmente entre 35 e 85 no matiz
VERDE_BAIXO = np.array([35, 80, 40])
VERDE_ALTO  = np.array([85, 255, 255])

# Vermelho: fica nas duas pontas da escala (perto de 0 e perto de 180)
VERMELHO_BAIXO_1 = np.array([0, 100, 40])
VERMELHO_ALTO_1  = np.array([10, 255, 255])
VERMELHO_BAIXO_2 = np.array([170, 100, 40])
VERMELHO_ALTO_2  = np.array([180, 255, 255])


def criar_mascaras(frame_hsv):
    # Máscara do verde
    mask_verde = cv2.inRange(frame_hsv, VERDE_BAIXO, VERDE_ALTO)

    # Máscara do vermelho (duas faixas somadas)
    mask_vermelho_1 = cv2.inRange(frame_hsv, VERMELHO_BAIXO_1, VERMELHO_ALTO_1)
    mask_vermelho_2 = cv2.inRange(frame_hsv, VERMELHO_BAIXO_2, VERMELHO_ALTO_2)
    mask_vermelho = cv2.bitwise_or(mask_vermelho_1, mask_vermelho_2)

    return mask_verde, mask_vermelho


def limpar_mascara(mask):
    """Remove ruído usando operações morfológicas."""
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    return mask


def desenhar_contornos(frame, mask, cor_bgr, nome):
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contornos:
        area = cv2.contourArea(c)
        if area > 500:  # ignora ruídos pequenos
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), cor_bgr, 2)
            cv2.putText(frame, nome, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_bgr, 2)


def main():
    cap = cv2.VideoCapture(0)  # 0 = câmera padrão

    if not cap.isOpened():
        print("Não foi possível acessar a câmera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_verde, mask_vermelho = criar_mascaras(frame_hsv)
        mask_verde = limpar_mascara(mask_verde)
        mask_vermelho = limpar_mascara(mask_vermelho)

        # Desenha retângulos ao redor dos objetos detectados
        desenhar_contornos(frame, mask_verde, (0, 255, 0), "Verde")
        desenhar_contornos(frame, mask_vermelho, (0, 0, 255), "Vermelho")

        # Máscara combinada só para visualização
        mask_total = cv2.bitwise_or(mask_verde, mask_vermelho)
        resultado = cv2.bitwise_and(frame, frame, mask=mask_total)

        cv2.imshow("Camera", frame)
        cv2.imshow("Mascara (verde + vermelho)", mask_total)
        cv2.imshow("Resultado filtrado", resultado)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
