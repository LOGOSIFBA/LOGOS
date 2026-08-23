from flask import Flask, Response
import cv2
import numpy
import threading
import time

HOST = "0.0.0.0"
PORT = 5000
WIDTH = 1280  # Resolução HD
HEIGHT = 720  # Resolução HD

app = Flask(__name__)

# Configuração da câmera (mantido a 15 FPS para não travar)
cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 15) 
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

latest = None
lock = threading.Lock()

HTML = """<!doctype html><html><body style="margin:0;background:#000">
<img src="/video" style="width:100vw;height:100vh;object-fit:contain">
</body></html>"""

# ==========================================
# OS OLHOS (Funções exatas do seu amigo)
# ==========================================
def convert_to_grayscale(frame):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame_gray

def blur_frame(frame):
    frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
    return frame_blur

def apply_black_mask(frame):
    frame_black_mask = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return frame_black_mask

def get_roi(frame, region):
    height, width = frame.shape[:2]
    if region == "top":
        roi = frame[:int(height * 0.4), :]
    elif region == "bottom":
        roi = frame[int(height * 0.4):, :]
    return roi
# ==========================================

def process(frame):
    # Apenas o processamento de imagem (sem o "cérebro")
    roi = get_roi(frame, "bottom")
    gray = convert_to_grayscale(roi)
    blur = blur_frame(gray)
    mask = apply_black_mask(blur)

    # Retorna diretamente a máscara (imagem preta e branca) para o navegador
    return mask

def capture():
    global latest
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.01)
            continue
            
        # O frame agora vira a máscara em preto e branco
        frame = process(frame)
        
        # Qualidade do JPEG aumentada para 95 para imagem limpa
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if ok:
            with lock:
                latest = buf.tobytes()

def gen():
    while True:
        with lock:
            f = latest
        if f is None:
            time.sleep(0.01)
            continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f + b'\r\n')
        time.sleep(0.03)

@app.get("/")
def index():
    return HTML

@app.get("/video")
def video():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    threading.Thread(target=capture, daemon=True).start()
    print(f"Rodando em: http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, threaded=True)