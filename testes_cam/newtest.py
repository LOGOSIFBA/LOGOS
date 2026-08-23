from __future__ import annotations

import time
from threading import Lock

import cv2
from flask import Flask, Response, render_template_string


app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
camera.set(cv2.CAP_PROP_FPS, 30)

camera_lock = Lock()


PAGE = """
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Teste Camera</title>
    <style>
        body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background: #111827;
            color: #f9fafb;
            font-family: Arial, sans-serif;
        }
        main {
            width: min(96vw, 1280px);
        }
        h1 {
            margin: 0 0 12px;
            font-size: 22px;
            font-weight: 600;
        }
        img {
            display: block;
            width: 100%;
            height: auto;
            background: #000;
            border: 1px solid #374151;
        }
    </style>
</head>
<body>
    <main>
        <h1>Visualizacao da camera</h1>
        <img src="/video_feed" alt="Camera ao vivo">
    </main>
</body>
</html>
"""


def desenhar_fps(frame, fps: float):
    texto = f"FPS: {fps:0.1f}"
    cv2.rectangle(frame, (10, 10), (150, 48), (0, 0, 0), -1)
    cv2.putText(
        frame,
        texto,
        (18, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )


def gerar_frames():
    ultimo_frame = time.perf_counter()
    fps_suavizado = 0.0

    while True:
        with camera_lock:
            sucesso, frame = camera.read()

        if not sucesso:
            time.sleep(0.1)
            continue

        agora = time.perf_counter()
        delta = agora - ultimo_frame
        ultimo_frame = agora

        fps_atual = 1.0 / delta if delta > 0 else 0.0
        fps_suavizado = (
            fps_atual
            if fps_suavizado == 0.0
            else (fps_suavizado * 0.9) + (fps_atual * 0.1)
        )

        desenhar_fps(frame, fps_suavizado)

        sucesso, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not sucesso:
            continue

        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/video_feed")
def video_feed():
    return Response(
        gerar_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    print("Camera aberta:", camera.isOpened())
    app.run(host="0.0.0.0", port=5000, threaded=True)
