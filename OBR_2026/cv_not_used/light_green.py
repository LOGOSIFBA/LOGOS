import cv2
import numpy as np

CAMERA_INDEX = 1

AREA_MINIMA_BLOCO = 350
MIN_PIXELS_SEMENTE = 20

# ============================================================
# 1. PARÂMETROS VERDE CLARO / MÉDIO
# ============================================================
STRICT_LIGHT_GREEN_LOW = np.array([35, 110, 80])
STRICT_LIGHT_GREEN_HIGH = np.array([85, 255, 255])

RELAXED_LIGHT_GREEN_LOW = np.array([30, 70, 60])
RELAXED_LIGHT_GREEN_HIGH = np.array([90, 255, 255])

# ============================================================
# 2. PARÂMETROS VERDE ESCURO / TEAL
# Saturação e Brilho calibrados para rejeitar preto e cinza
# ============================================================
STRICT_DARK_GREEN_LOW = np.array([35, 75, 25])
STRICT_DARK_GREEN_HIGH = np.array([95, 255, 140])

RELAXED_DARK_GREEN_LOW = np.array([32, 55, 20])
RELAXED_DARK_GREEN_HIGH = np.array([100, 255, 155])


def remover_superesposicao_e_lampadas(frame_bgr, hsv_frame):
    b = frame_bgr[:, :, 0].astype(np.float32)
    g = frame_bgr[:, :, 1].astype(np.float32)
    r = frame_bgr[:, :, 2].astype(np.float32)

    s = hsv_frame[:, :, 1]
    v = hsv_frame[:, :, 2]

    # Bloqueia regiões brilhantes e pouco saturadas (lâmpada/brilho seco)
    lampada_ou_reflexo = (v > 170) & (s < 70)

    # Bloqueia superexposição branca (R, G, B altos e próximos)
    branco_estourado = (r > 160) & (g > 160) & (b > 160) & ((g - r) < 25.0)

    mascara_invalida = lampada_ou_reflexo | branco_estourado
    return (~mascara_invalida).astype(np.uint8) * 255


def filtro_bgr_verde_claro(frame_bgr):
    b = frame_bgr[:, :, 0].astype(np.float32)
    g = frame_bgr[:, :, 1].astype(np.float32)
    r = frame_bgr[:, :, 2].astype(np.float32)

    cond_r = g > (r * 1.25)
    cond_b = g > (b * 1.15)
    diferenca = (g - r > 20.0) & (g - b > 15.0) & (g > 60.0)
    return (cond_r & cond_b & diferenca).astype(np.uint8) * 255


def filtro_bgr_verde_escuro(frame_bgr, modo="strict"):
    b = frame_bgr[:, :, 0].astype(np.float32)
    g = frame_bgr[:, :, 1].astype(np.float32)
    r = frame_bgr[:, :, 2].astype(np.float32)

    if modo == "strict":
        # Exige dominância de Green sobre Red e Blue + valor mínimo para travar a pista preta
        cond_r = (g - r) >= 8.0
        cond_b = (g - b) >= 4.0
        cond_g_val = g >= 22.0
        return (cond_r & cond_b & cond_g_val).astype(np.uint8) * 255
    else:
        cond_r = (g - r) >= 5.0
        cond_b = (g - b) >= 2.0
        cond_g_val = g >= 18.0
        return (cond_r & cond_b & cond_g_val).astype(np.uint8) * 255


def expandir_por_semente(mask_strict, mask_relaxed):
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_strict = cv2.morphologyEx(
        mask_strict, cv2.MORPH_OPEN, kernel_small, iterations=1
    )

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask_relaxed, connectivity=8
    )
    mask_final = np.zeros_like(mask_relaxed)

    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < AREA_MINIMA_BLOCO:
            continue

        component_mask = (labels == i).astype(np.uint8) * 255
        intersecao = cv2.bitwise_and(component_mask, mask_strict)

        if cv2.countNonZero(intersecao) >= MIN_PIXELS_SEMENTE:
            mask_final[labels == i] = 255

    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    return cv2.morphologyEx(
        mask_final, cv2.MORPH_CLOSE, kernel_close, iterations=1
    )


def detectar_verde_completo(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    trava_anti_brilho = remover_superesposicao_e_lampadas(frame, hsv)

    # 1. PROCESSA VERDE CLARO
    trava_clara = cv2.bitwise_and(
        filtro_bgr_verde_claro(frame), trava_anti_brilho
    )
    s_light = cv2.bitwise_and(
        cv2.inRange(hsv, STRICT_LIGHT_GREEN_LOW, STRICT_LIGHT_GREEN_HIGH),
        trava_clara,
    )
    r_light = cv2.bitwise_and(
        cv2.inRange(hsv, RELAXED_LIGHT_GREEN_LOW, RELAXED_LIGHT_GREEN_HIGH),
        trava_clara,
    )
    mask_verde_claro = expandir_por_semente(s_light, r_light)

    # 2. PROCESSA VERDE ESCURO / TEAL
    trava_escura_s = cv2.bitwise_and(
        filtro_bgr_verde_escuro(frame, modo="strict"), trava_anti_brilho
    )
    trava_escura_r = cv2.bitwise_and(
        filtro_bgr_verde_escuro(frame, modo="relaxed"), trava_anti_brilho
    )

    s_dark = cv2.bitwise_and(
        cv2.inRange(hsv, STRICT_DARK_GREEN_LOW, STRICT_DARK_GREEN_HIGH),
        trava_escura_s,
    )
    r_dark = cv2.bitwise_and(
        cv2.inRange(hsv, RELAXED_DARK_GREEN_LOW, RELAXED_DARK_GREEN_HIGH),
        trava_escura_r,
    )
    mask_verde_escuro = expandir_por_semente(s_dark, r_dark)

    # 3. MÁSCARA UNIFICADA FINAL
    mask_verde_unificada = cv2.bitwise_or(mask_verde_claro, mask_verde_escuro)

    return mask_verde_unificada, mask_verde_claro, mask_verde_escuro


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

        mask_final, mask_claro, mask_escuro = detectar_verde_completo(frame)

        contornos, _ = cv2.findContours(
            mask_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for c in contornos:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                "Verde Detectado",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Mascara Verde Claro", mask_claro)
        cv2.imshow("Mascara Verde Escuro", mask_escuro)
        cv2.imshow("Mascara Unificada Final", mask_final)
        cv2.imshow("Deteccao Visual", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()