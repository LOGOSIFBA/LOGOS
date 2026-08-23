import cv2

cap = cv2.VideoCapture(0)

print("Camera aberta:", cap.isOpened())

ret, frame = cap.read()

print("Leitura:", ret)

cap.release()
