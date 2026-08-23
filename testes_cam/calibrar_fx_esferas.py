"""
Calibracao de fx (distancia focal em pixels) usando esferas ou objetos circulares.

Diferenca da calibracao com retangulos:
 - Usa cv2.HoughCircles em vez de contornos/boundingRect
 - A medida usada e o DIAMETRO do circulo (nao largura/altura de bounding box)
 - Ao final, tambem calcula o FOV horizontal real da camera, derivado do fx medio

Como funciona:
 1. Aponte a esfera para a camera
 2. Quando o circulo verde estiver bem ajustado na esfera, pressione 'c'
 3. Digite no terminal: a distancia real (cm) e o diametro real do objeto (cm)
 4. O script calcula fx automaticamente e guarda
 5. Repita em varias distancias (recomendado: 4-5 medicoes)
 6. Pressione 'q' para sair e ver a media final de fx + o FOV calculado

Pressione 'r' a qualquer momento para ver o resumo parcial.
"""

import cv2
import numpy as np
import math

# ---------- CONFIGURACOES ----------
CAMERA_INDEX = 1
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Parametros do HoughCircles (ajuste conforme necessario)
DP = 1.2
MIN_DIST = 50
PARAM1 = 90
PARAM2 = 50
MIN_RADIUS = 50
MAX_RADIUS = 400
# ------------------------------------

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # troque para cv2.CAP_DSHOW se estiver no Windows
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    print("Erro: nao foi possivel abrir a camera.")
    exit()

medicoes = []  # cada item: (fx_calculado, distancia, diametro_real_cm, diametro_px)

print("=" * 65)
print("CALIBRACAO DE fx COM ESFERAS / OBJETOS CIRCULARES")
print("Pressione 'c' para capturar uma medicao")
print("Pressione 'r' para ver o resumo parcial")
print("Pressione 'q' para sair e ver o resultado final (fx + FOV)")
print("=" * 65)


def calcular_fov_graus(fx, largura_frame_px):
    """
    FOV horizontal (graus) a partir de fx e da largura do frame em pixels.
    FOV = 2 * atan( (largura_frame/2) / fx )
    """
    fov_rad = 2 * math.atan((largura_frame_px / 2) / fx)
    return math.degrees(fov_rad)


def mostrar_resumo():
    if not medicoes:
        print("\nNenhuma medicao registrada ainda.\n")
        return
    print("\n" + "-" * 70)
    print(f"{'Dist(cm)':>10} | {'Diam_real(cm)':>13} | {'diam_px':>8} | {'fx':>10}")
    print("-" * 70)
    soma = 0
    for fx, dist, d_real, d_px in medicoes:
        print(f"{dist:>10.1f} | {d_real:>13.1f} | {d_px:>8} | {fx:>10.2f}")
        soma += fx
    media = soma / len(medicoes)
    fov = calcular_fov_graus(media, FRAME_WIDTH)
    print("-" * 70)
    print(f"Media de fx ({len(medicoes)} medicoes): {media:.2f} px")
    print(f"FOV horizontal calculado: {fov:.2f} graus  (para largura de frame = {FRAME_WIDTH}px)")
    print("-" * 70 + "\n")


while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=DP,
        minDist=MIN_DIST,
        param1=PARAM1,
        param2=PARAM2,
        minRadius=MIN_RADIUS,
        maxRadius=MAX_RADIUS
    )

    diametro_px = None

    if circles is not None:
        circles_arr = np.round(circles[0, :]).astype("int")
        maior = max(circles_arr, key=lambda c: c[2])
        cx, cy, r = maior
        diametro_px = r * 2

        cv2.circle(frame, (cx, cy), r, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
        texto = f"diametro={diametro_px}px"
        cv2.putText(frame, texto, (cx - r, max(cy - r - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    status = f"Medicoes: {len(medicoes)}  |  'c' capturar  'r' resumo  'q' sair"
    cv2.putText(frame, status, (10, FRAME_HEIGHT - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow("Camera", frame)
    #cv2.imshow("Blur (entrada do Hough)", blur)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    elif key == ord('r'):
        mostrar_resumo()

    elif key == ord('c'):
        if diametro_px is None:
            print("Nenhum objeto circular detectado no momento. Ajuste a posicao/parametros do Hough e tente de novo.")
            continue
        try:
            print(f"\nCaptura: diametro={diametro_px}px")
            dist_str = input("Digite a distancia REAL ate o objeto (cm): ").strip()
            d_real_str = input("Digite o DIAMETRO REAL do objeto (cm): ").strip()
            dist = float(dist_str.replace(",", "."))
            d_real = float(d_real_str.replace(",", "."))

            fx = (diametro_px * dist) / d_real
            medicoes.append((fx, dist, d_real, diametro_px))
            print(f"-> fx calculado: {fx:.2f} px  (medicao #{len(medicoes)} registrada)\n")
        except ValueError:
            print("Entrada invalida, tente novamente com numeros (ex: 20 ou 20.5).\n")

cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 65)
print("RESUMO FINAL DA CALIBRACAO")
print("=" * 65)
mostrar_resumo()

if medicoes:
    fx_medio = sum(m[0] for m in medicoes) / len(medicoes)
    fov_final = calcular_fov_graus(fx_medio, FRAME_WIDTH)
    print(f"\n>>> fx = {fx_medio:.2f} px")
    print(f">>> FOV horizontal real da camera = {fov_final:.2f} graus")
    print(">>> Use esses valores no seu codigo de calculo de distancia <<<\n")
