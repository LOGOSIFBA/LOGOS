import cv2
import numpy as np

CAMERA_INDEX = 1
AREA_MINIMA = 1300

# ============================================================
# FAIXAS MAIS RÍGIDAS EXCLUSIVAS PARA O VERDE ESCURO
# - H (82-98): Afastado ainda mais do verde claro (H <= 75)
# - S (75-255): Exige mais saturação (elimina pretos/cinzas residuais)
# - V (25-95) : Teto reduzido para 95 (bloqueia o verde claro na hora)
# ============================================================
LOWER_DARK_GREEN = np.array([82, 75, 25])
UPPER_DARK_GREEN = np.array([98, 255, 95])


def detectar_somente_verde_escuro(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 1. Filtro HSV mais estrito
    mask_hsv = cv2.inRange(hsv, LOWER_DARK_GREEN, UPPER_DARK_GREEN)

    # 2. Trava de Canais BGR (Rigidez aumentada)
    b = frame[:, :, 0].astype(np.float32)
    g = frame[:, :, 1].astype(np.float32)
    r = frame[:, :, 2].astype(np.float32)

    # Dominância do verde reforçada (+1 na diferença)
    cond_verde_dominante = (g - r) >= 16.0

    # Azul perceptivelmente maior que vermelho (garante o tom frio/escuro e bloqueia verde claro)
    cond_tom_teal = (b - r) >= 2.0

    # Faixa de G restrita: Teto em 90 mata qualquer presença de verde claro
    cond_faixa_g = (g >= 32.0) & (g <= 90.0)

    mask_bgr = (
        cond_verde_dominante & cond_tom_teal & cond_faixa_g
    ).astype(np.uint8) * 255

    # Interseção HSV + BGR
    mask_combinada = cv2.bitwise_and(mask_hsv, mask_bgr)

    # 3. Limpeza Morfológica
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

    mask_limpa = cv2.morphologyEx(mask_combinada, cv2.MORPH_OPEN, kernel_open)
    mask_limpa = cv2.morphologyEx(mask_limpa, cv2.MORPH_CLOSE, kernel_close)

    # 4. Filtragem por área e preenchimento sólido
    contornos, _ = cv2.findContours(
        mask_limpa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    mask_final = np.zeros_like(mask_limpa)

    for c in contornos:
        if cv2.contourArea(c) >= AREA_MINIMA:
            cv2.drawContours(mask_final, [c], -1, 255, thickness=cv2.FILLED)

    return mask_final


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        return

    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_AUTO_WB, 0)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        mask_escuro = detectar_somente_verde_escuro(frame)

        contornos, _ = cv2.findContours(
            mask_escuro, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for c in contornos:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                "Verde Escuro",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Mascara Verde Escuro", mask_escuro)
        cv2.imshow("Deteccao Visual", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()