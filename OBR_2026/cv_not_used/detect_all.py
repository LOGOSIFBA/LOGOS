import cv2
import numpy as np

CAMERA_INDEX = 1

# ============================================================
# 1. PARÂMETROS VERMELHO (Anti-Laranja / Semente + Expansão)
# ============================================================
RED_AREA_MINIMA_BLOCO = 600
RED_MIN_PIXELS_SEMENTE = 40

STRICT_RED_LOW_1 = np.array([0, 175, 70])
STRICT_RED_HIGH_1 = np.array([2, 255, 255])

STRICT_RED_LOW_2 = np.array([176, 175, 70])
STRICT_RED_HIGH_2 = np.array([180, 255, 255])

RELAXED_RED_LOW_1 = np.array([0, 80, 30])
RELAXED_RED_HIGH_1 = np.array([6, 255, 255])

RELAXED_RED_LOW_2 = np.array([168, 80, 30])
RELAXED_RED_HIGH_2 = np.array([180, 255, 255])

# ============================================================
# 2. PARÂMETROS VERDE CLARO
# ============================================================
LIGHT_GREEN_AREA_MINIMA = 350
LIGHT_GREEN_MIN_SEMENTE = 20

STRICT_LIGHT_GREEN_LOW = np.array([35, 110, 80])
STRICT_LIGHT_GREEN_HIGH = np.array([85, 255, 255])

RELAXED_LIGHT_GREEN_LOW = np.array([30, 70, 60])
RELAXED_LIGHT_GREEN_HIGH = np.array([90, 255, 255])

# ============================================================
# 3. PARÂMETROS VERDE ESCURO EXCLUSIVO (Rigidez Máxima)
# ============================================================
DARK_GREEN_AREA_MINIMA = 1300

LOWER_DARK_GREEN = np.array([82, 75, 25])
UPPER_DARK_GREEN = np.array([98, 255, 95])


# ============================================================
# FUNÇÕES - VERMELHO
# ============================================================
def filtro_anti_laranja_matematico(frame_bgr):
  b = frame_bgr[:, :, 0].astype(np.float32)
  g = frame_bgr[:, :, 1].astype(np.float32)
  r = frame_bgr[:, :, 2].astype(np.float32)

  soma_rgb = r + g + b + 1e-5
  norm_r = r / soma_rgb
  razao_rg = r / (g + 1e-5)

  cond_razao = razao_rg > 3.8
  cond_norm = norm_r > 0.68
  cond_green_cap = g < 65.0

  mask_anti_laranja = (
      (cond_razao & cond_norm & cond_green_cap).astype(np.uint8) * 255
  )
  return mask_anti_laranja


def detectar_vermelho(frame, hsv):
  m_strict1 = cv2.inRange(hsv, STRICT_RED_LOW_1, STRICT_RED_HIGH_1)
  m_strict2 = cv2.inRange(hsv, STRICT_RED_LOW_2, STRICT_RED_HIGH_2)
  mask_strict_hsv = cv2.bitwise_or(m_strict1, m_strict2)

  mask_anti_laranja = filtro_anti_laranja_matematico(frame)
  mask_strict = cv2.bitwise_and(mask_strict_hsv, mask_anti_laranja)

  m_relaxed1 = cv2.inRange(hsv, RELAXED_RED_LOW_1, RELAXED_RED_HIGH_1)
  m_relaxed2 = cv2.inRange(hsv, RELAXED_RED_LOW_2, RELAXED_RED_HIGH_2)
  mask_relaxed = cv2.bitwise_or(m_relaxed1, m_relaxed2)

  kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  mask_strict = cv2.morphologyEx(
      mask_strict, cv2.MORPH_OPEN, kernel_small, iterations=1
  )

  num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
      mask_relaxed, connectivity=8
  )
  mask_final = np.zeros_like(mask_relaxed)

  for i in range(1, num_labels):
    if stats[i, cv2.CC_STAT_AREA] < RED_AREA_MINIMA_BLOCO:
      continue

    component_mask = (labels == i).astype(np.uint8) * 255
    intersecao = cv2.bitwise_and(component_mask, mask_strict)

    if cv2.countNonZero(intersecao) >= RED_MIN_PIXELS_SEMENTE:
      mask_final[labels == i] = 255

  kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
  mask_final = cv2.morphologyEx(
      mask_final, cv2.MORPH_CLOSE, kernel_close, iterations=2
  )

  return mask_final


# ============================================================
# FUNÇÕES - VERDE CLARO
# ============================================================
def remover_superesposicao_e_lampadas(frame_bgr, hsv_frame):
  b = frame_bgr[:, :, 0].astype(np.float32)
  g = frame_bgr[:, :, 1].astype(np.float32)
  r = frame_bgr[:, :, 2].astype(np.float32)

  s = hsv_frame[:, :, 1]
  v = hsv_frame[:, :, 2]

  lampada_ou_reflexo = (v > 170) & (s < 70)
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


def detectar_verde_claro(frame, hsv):
  trava_anti_brilho = remover_superesposicao_e_lampadas(frame, hsv)
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

  kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  s_light = cv2.morphologyEx(s_light, cv2.MORPH_OPEN, kernel_small, iterations=1)

  num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
      r_light, connectivity=8
  )
  mask_final = np.zeros_like(r_light)

  for i in range(1, num_labels):
    if stats[i, cv2.CC_STAT_AREA] < LIGHT_GREEN_AREA_MINIMA:
      continue

    component_mask = (labels == i).astype(np.uint8) * 255
    intersecao = cv2.bitwise_and(component_mask, s_light)

    if cv2.countNonZero(intersecao) >= LIGHT_GREEN_MIN_SEMENTE:
      mask_final[labels == i] = 255

  kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
  return cv2.morphologyEx(
      mask_final, cv2.MORPH_CLOSE, kernel_close, iterations=1
  )


# ============================================================
# FUNÇÕES - VERDE ESCURO EXCLUSIVO
# ============================================================
def detectar_somente_verde_escuro(frame, hsv):
  mask_hsv = cv2.inRange(hsv, LOWER_DARK_GREEN, UPPER_DARK_GREEN)

  b = frame[:, :, 0].astype(np.float32)
  g = frame[:, :, 1].astype(np.float32)
  r = frame[:, :, 2].astype(np.float32)

  cond_verde_dominante = (g - r) >= 16.0
  cond_tom_teal = (b - r) >= 2.0
  cond_faixa_g = (g >= 32.0) & (g <= 90.0)

  mask_bgr = (
      cond_verde_dominante & cond_tom_teal & cond_faixa_g
  ).astype(np.uint8) * 255

  mask_combinada = cv2.bitwise_and(mask_hsv, mask_bgr)

  kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
  kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

  mask_limpa = cv2.morphologyEx(mask_combinada, cv2.MORPH_OPEN, kernel_open)
  mask_limpa = cv2.morphologyEx(mask_limpa, cv2.MORPH_CLOSE, kernel_close)

  contornos, _ = cv2.findContours(
      mask_limpa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )
  mask_final = np.zeros_like(mask_limpa)

  for c in contornos:
    if cv2.contourArea(c) >= DARK_GREEN_AREA_MINIMA:
      cv2.drawContours(mask_final, [c], -1, 255, thickness=cv2.FILLED)

  return mask_final


# ============================================================
# MAIN
# ============================================================
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

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Execução das detecções
    mask_vermelho = detectar_vermelho(frame, hsv)
    mask_verde_claro = detectar_verde_claro(frame, hsv)
    mask_verde_escuro = detectar_somente_verde_escuro(frame, hsv)

    # 1. Contornos - Vermelho
    contornos_red, _ = cv2.findContours(
        mask_vermelho, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for c in contornos_red:
      x, y, w, h = cv2.boundingRect(c)
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
      cv2.putText(
          frame,
          "Vermelho Validado",
          (x, max(y - 10, 20)),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.6,
          (0, 0, 255),
          2,
      )

    # 2. Contornos - Verde Claro
    contornos_v_claro, _ = cv2.findContours(
        mask_verde_claro, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for c in contornos_v_claro:
      x, y, w, h = cv2.boundingRect(c)
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 128), 2)
      cv2.putText(
          frame,
          "Verde Claro",
          (x, max(y - 10, 20)),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.6,
          (0, 255, 128),
          2,
      )

    # 3. Contornos - Verde Escuro
    contornos_v_escuro, _ = cv2.findContours(
        mask_verde_escuro, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for c in contornos_v_escuro:
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

    # Exibição
    cv2.imshow("Mascara Vermelho", mask_vermelho)
    cv2.imshow("Mascara Verde Claro", mask_verde_claro)
    cv2.imshow("Mascara Verde Escuro", mask_verde_escuro)
    cv2.imshow("Deteccao Visual Unificada", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
      break

  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()