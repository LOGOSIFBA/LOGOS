import cv2
import numpy as np

camera = cv2.VideoCapture(1)
centro = 639 / 2

while True:
    ret, frame = camera.read()
    imgcinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # imgblur = cv2.GaussianBlur(imgcinza, (3, 3), 2)

    circulos = cv2.HoughCircles (
        imgcinza,
        cv2.HOUGH_GRADIENT,
        dp = 1,
        minDist = 50,
        param1 = 99,
        param2 = 79,
        minRadius = 10,
        maxRadius = 200
    )

    if circulos is not None:
        circulos = np.round(circulos[0, :]).astype("int")
        for x, y, raio in circulos:
            cv2.circle(frame, (x,y), raio, (255, 0, 255), 2)

    cv2.imshow("Circles", frame)
    cv2.waitKey(1)

camera.release()
cv2.destroyAllWindows()