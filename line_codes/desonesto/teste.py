import cv2
index = 1
cap = cv2.VideoCapture(index)

if not cap.isOpened():
    print("Não abriu a câmera.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Erro ao ler câmera")
        break

    cv2.imshow("Logitech", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()