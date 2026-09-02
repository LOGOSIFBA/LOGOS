import cv2
import numpy as np

CAMERA_INDEX = 1

AREA_MINIMA_BLOCO = 600
MIN_PIXELS_SEMENTE = 40

# ============================================================
# 1. LIMIARES HSV DE SEMENTE (Extremamente Restritos)
# ============================================================
STRICT_LOW_1 = np.array([0, 175, 70])
STRICT_HIGH_1 = np.array([2, 255, 255])

STRICT_LOW_2 = np.array([176, 175, 70])
STRICT_HIGH_2 = np.array([180, 255, 255])

# ============================================================
# 2. LIMIARES HSV RELAXADOS (Corpo do Objeto e Sombras Internas)
# ============================================================
RELAXED_LOW_1 = np.array([0, 80, 30])
RELAXED_HIGH_1 = np.array([6, 255, 255])

RELAXED_LOW_2 = np.array([168, 80, 30])
RELAXED_HIGH_2 = np.array([180, 255, 255])


def filtro_anti_laranja_matematico(frame_bgr):
    """Filtro físico de canais BGR que torna matematicamente impossível o tom laranja gerar sementes de validação."""
    b = frame_bgr[:, :, 0].astype(np.float32)
    g = frame_bgr[:, :, 1].astype(np.float32)
    r = frame_bgr[:, :, 2].astype(np.float32)

    soma_rgb = r + g + b + 1e-5
    norm_r = r / soma_rgb
    razao_rg = r / (g + 1e-5)

    # 1. Exige que Red seja quase 4x maior que Green
    cond_razao = razao_rg > 3.8
    # 2. Exige dominância absoluta de Red no pixel (> 68%)
    cond_norm = norm_r > 0.68
    # 3. Corta o canal Green (Laranja possui Green entre 80 e 150)
    cond_green_cap = g < 65.0

    mask_anti_laranja = (
        (cond_razao & cond_norm & cond_green_cap).astype(np.uint8) * 255
    )
    return mask_anti_laranja


def reconstruir_objeto_por_semente(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 1. Máscara de Semente HSV
    m_strict1 = cv2.inRange(hsv, STRICT_LOW_1, STRICT_HIGH_1)
    m_strict2 = cv2.inRange(hsv, STRICT_LOW_2, STRICT_HIGH_2)
    mask_strict_hsv = cv2.bitwise_or(m_strict1, m_strict2)

    # 2. Trava Física BGR Anti-Laranja aplicada às Sementes
    mask_anti_laranja = filtro_anti_laranja_matematico(frame)
    mask_strict = cv2.bitwise_and(mask_strict_hsv, mask_anti_laranja)

    # 3. Máscara Relaxada para Expansão
    m_relaxed1 = cv2.inRange(hsv, RELAXED_LOW_1, RELAXED_HIGH_1)
    m_relaxed2 = cv2.inRange(hsv, RELAXED_LOW_2, RELAXED_HIGH_2)
    mask_relaxed = cv2.bitwise_or(m_relaxed1, m_relaxed2)

    # Limpeza morfológica nas sementes
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_strict = cv2.morphologyEx(
        mask_strict, cv2.MORPH_OPEN, kernel_small, iterations=1
    )

    # Reconstrução geodésica por componentes conectados
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask_relaxed, connectivity=8
    )
    mask_final = np.zeros_like(mask_relaxed)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < AREA_MINIMA_BLOCO:
            continue

        component_mask = (labels == i).astype(np.uint8) * 255
        intersecao = cv2.bitwise_and(component_mask, mask_strict)

        # O bloco só expande se contiver sementes validadas pela trava BGR
        if cv2.countNonZero(intersecao) >= MIN_PIXELS_SEMENTE:
            mask_final[labels == i] = 255

    # Preenchimento de furos
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask_final = cv2.morphologyEx(
        mask_final, cv2.MORPH_CLOSE, kernel_close, iterations=2
    )

    return mask_final, mask_strict, mask_relaxed


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

        mask_final, mask_strict, mask_relaxed = reconstruir_objeto_por_semente(
            frame
        )

        contornos, _ = cv2.findContours(
            mask_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for c in contornos:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                "Vermelho Validado",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.imshow("1. Sementes Rigidas (Zero Laranja)", mask_strict)
        cv2.imshow("2. Mascara Relaxada", mask_relaxed)
        cv2.imshow("3. Expansao Final", mask_final)
        cv2.imshow("Resultado Visual", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()