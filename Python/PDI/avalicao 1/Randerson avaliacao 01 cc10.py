import cv2
import numpy as np

cap = cv2.VideoCapture('avalicao 1/IFMA Campus Caxias.mp4')

lower_color = np.array([35, 50, 50])
upper_color = np.array([85, 255, 255])

while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    color_region = cv2.bitwise_and(frame, frame, mask=mask)
    _, mask_inv = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY_INV)
    gray_region = cv2.bitwise_and(gray_bgr, gray_bgr, mask=mask_inv)
    result = cv2.add(color_region, gray_region)

    cv2.imshow('Result', result)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()