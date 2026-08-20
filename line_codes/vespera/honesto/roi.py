import cv2
index = 1
camera = cv2.VideoCapture(index)

while True:
    ret, frame = camera.read()
    cv2.imshow("areazinha linda", frame)
    cv2.waitKey(1)
    x, y, w, h = cv2.selectROI("Selecionar ROI", frame)
    print(x, y, w, h)

cv2.destroyAllWindows()