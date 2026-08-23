"""
Servidor Flask com streaming MJPEG da camera processada.

Mostra no navegador (http://IP_DO_RASP:5000) a imagem da camera
com a esfera detectada (circulo verde) e a distancia estimada escrita na imagem.

Rodar no Raspberry:
    python3 app.py

Acessar do seu Windows (mesma rede):
    http://IP_DO_RASPBERRY:5000
"""

import cv2
import numpy as np
from flask import Flask, Response

# ---------- CONFIGURACOES ----------
CAMERA_INDEX = 0
FRAME_WIDTH = 640          # resolucao menor = mais FPS no Raspberry
FRAME_HEIGHT = 480

FX = 1547.0                 # fx calibrado (px)
DIAMETRO_REAL_CM = 6.7       # diametro real da esfera (cm) - AJUSTE conforme a esfera usada

DP = 1.2
MIN_DIST = 100
PARAM1 = 90
PARAM2 = 50
MIN_RADIUS = 15
MAX_RADIUS = 300
# ------------------------------------

app = Flask(__name__)

# No Linux/Raspberry, cv2.CAP_V4L2 e o backend correto (equivalente ao CAP_DSHOW do Windows)
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    raise RuntimeError("Nao foi possivel abrir a camera. Verifique /dev/video0 com 'ls /dev/video*'.")


def processar_frame(frame):
    """Detecta a esfera, calcula a distancia e desenha tudo no frame."""
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

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        maior = max(circles, key=lambda c: c[2])
        cx, cy, r = maior
        diametro_px = r * 2

        if diametro_px > 0:
            distancia_cm = (DIAMETRO_REAL_CM * FX) / diametro_px

            cv2.circle(frame, (cx, cy), r, (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

            cv2.putText(frame, f"diametro={diametro_px}px", (cx - r, max(cy - r - 30, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Distancia: {distancia_cm:.1f} cm", (cx - r, max(cy - r - 5, 40)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    else:
        cv2.putText(frame, "Nenhuma esfera detectada", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return frame


def gerar_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = processar_frame(frame)

        ok, buffer = cv2.imencode('.jpg', frame)
        if not ok:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    # Pagina minima: so a imagem, sem nada em volta
    return """
    <html>
        <head><title>Camera - Distancia da Esfera</title></head>
        <body style="margin:0; background:#000;">
            <img src="/video_feed" style="width:100%; height:auto; display:block;">
        </body>
    </html>
    """


@app.route('/video_feed')
def video_feed():
    return Response(gerar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # host='0.0.0.0' permite acessar de outros dispositivos na rede (nao so do proprio Rasp)
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)