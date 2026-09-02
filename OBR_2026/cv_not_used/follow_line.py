import cv2
import numpy as np

CAMERA_INDEX = 1

# ROI (Região de Interesse): Foca apenas na parte inferior da imagem para seguir a linha
ROI_ALTURA_PERCENTUAL = 0.4  # Pega os 40% inferiores do frame
AREA_MINIMA_LINHA = 800  # Ignora sujeiras/ruídos pretos pequenos

# Limite HSV para Preto (Baixo Valor/Brilho)
LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([180, 110, 50])  # V <= 50 garante apenas tons muito escuros


def isolar_linha_preta(frame):
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  # 1. Filtro HSV para tons escuros
  mask_hsv = cv2.inRange(hsv, LOWER_BLACK, UPPER_BLACK)

  # 2. Trava Físico-Matemática BGR
  # Exige brilho baixo e neutralidade de cor (impede que Verde Escuro ou Azul Escuro passem)
  b = frame[:, :, 0].astype(np.float32)
  g = frame[:, :, 1].astype(np.float32)
  r = frame[:, :, 2].astype(np.float32)

  cond_brilho_baixo = (r <= 50.0) & (g <= 50.0) & (b <= 50.0)

  # Neutralidade cromática: a diferença entre os canais deve ser pequena (sem cor dominante)
  max_canal = np.maximum(r, np.maximum(g, b))
  min_canal = np.minimum(r, np.minimum(g, b))
  cond_sem_cor = (max_canal - min_canal) <= 12.0

  mask_bgr = (cond_brilho_baixo & cond_sem_cor).astype(np.uint8) * 255

  # Interseção HSV + BGR
  mask_preto = cv2.bitwise_and(mask_hsv, mask_bgr)

  # 3. Limpeza morfológica para unificar a linha
  kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
  kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

  mask_limpa = cv2.morphologyEx(mask_preto, cv2.MORPH_OPEN, kernel_open)
  mask_limpa = cv2.morphologyEx(mask_limpa, cv2.MORPH_CLOSE, kernel_close)

  return mask_limpa


def processar_seguidor_linha(frame):
  h, w, _ = frame.shape
  centro_frame_x = w // 2

  # Definir ROI (Região de Interesse) na parte inferior da tela
  roi_y_inicio = int(h * (1.0 - ROI_ALTURA_PERCENTUAL))
  roi_frame = frame[roi_y_inicio:h, 0:w]

  # Isolar linha preta apenas na ROI
  mask_preto_roi = isolar_linha_preta(roi_frame)

  # Encontrar contornos na ROI
  contornos, _ = cv2.findContours(
      mask_preto_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )

  centro_linha_x = None
  erro = 0
  direcao = 'LINHA NAO ENCONTRADA'

  if contornos:
    # Seleciona o maior contorno encontrado dentro da ROI (a linha principal)
    maior_contorno = max(contornos, key=cv2.contourArea)

    if cv2.contourArea(maior_contorno) >= AREA_MINIMA_LINHA:
      # Calculo do Centro de Massa (Centroide X) da linha
      M = cv2.moments(maior_contorno)
      if M['m00'] > 0:
        centro_linha_x = int(M['m10'] / M['m00'])
        centro_linha_y_roi = int(M['m01'] / M['m00'])
        centro_linha_y_global = centro_linha_y_roi + roi_y_inicio

        # Erro de desvio em relação ao centro do robô/câmera
        erro = centro_linha_x - centro_frame_x

        # Tolerância central
        if abs(erro) <= 20:
          direcao = 'FRENTE'
        elif erro < -20:
          direcao = 'ESQUERDA'
        else:
          direcao = 'DIREITA'

        # Desenhar contorno da linha na ROI (coordenadas adaptadas para o frame global)
        maior_contorno_global = maior_contorno + np.array([0, roi_y_inicio])
        cv2.drawContours(frame, [maior_contorno_global], -1, (0, 255, 0), 2)

        # Desenhar ponto central da linha
        cv2.circle(
            frame,
            (centro_linha_x, centro_linha_y_global),
            6,
            (0, 0, 255),
            -1,
        )

        # Linha guia conectando o centro da tela ao centro da linha
        cv2.line(
            frame,
            (centro_frame_x, centro_linha_y_global),
            (centro_linha_x, centro_linha_y_global),
            (255, 0, 0),
            2,
        )

  # Desenhar ROI na tela
  cv2.rectangle(
      frame, (0, roi_y_inicio), (w - 1, h - 1), (255, 255, 0), 2
  )  # Moldura Amarela
  cv2.line(
      frame, (centro_frame_x, 0), (centro_frame_x, h), (100, 100, 100), 1
  )  # Eixo central vertical

  # Exibir informações na tela
  cv2.putText(
      frame,
      f'Direcao: {direcao}',
      (20, 35),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.8,
      (0, 255, 255),
      2,
  )
  cv2.putText(
      frame,
      f'Erro X: {erro} px',
      (20, 70),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.7,
      (255, 255, 255),
      2,
  )

  return frame, mask_preto_roi


def main():
  cap = cv2.VideoCapture(CAMERA_INDEX)

  if not cap.isOpened():
    print('Erro ao acessar a câmera.')
    return

  cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
  cap.set(cv2.CAP_PROP_AUTO_WB, 0)

  while True:
    ret, frame = cap.read()
    if not ret or frame is None:
      break

    frame_processado, mascara_preta = processar_seguidor_linha(frame)

    cv2.imshow('Mascara Linha Preta (ROI)', mascara_preta)
    cv2.imshow('Seguidor de Linha Preto', frame_processado)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  cv2.destroyAllWindows()


if __name__ == '__main__':
  main()