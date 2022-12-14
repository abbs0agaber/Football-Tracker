from collections import deque
import cv2
from cv2 import minEnclosingCircle
import imutils
import numpy as np
import time

prev_time = time.time()
points = deque(maxlen=20)

def test(v):
    pass

vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
fourcc = cv2.VideoWriter_fourcc(*"MJPG")
vc.set(cv2.CAP_PROP_FOURCC, fourcc)
vc.set(cv2.CAP_PROP_FPS, 30)


cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.namedWindow("result", cv2.WINDOW_NORMAL)

cv2.createTrackbar("min_h", "result", 138, 255, test)
cv2.createTrackbar("min_s", "result", 123, 255, test)
cv2.createTrackbar("min_v", "result", 147, 255, test)


cv2.createTrackbar("max_h", "result", 175, 255, test)
cv2.createTrackbar("max_s", "result", 255, 255, test)
cv2.createTrackbar("max_v", "result", 255, 255, test)

cv2.createTrackbar("dilate", "result", 2, 16, test)
cv2.createTrackbar("erode", "result", 2, 16, test)

if vc.isOpened():  # try to get the first frame
    rval, frame = vc.read()
    cv2.imshow("frame",frame)
else:
    rval = False

while rval:
    rval, frame = vc.read()

    min_h = cv2.getTrackbarPos("min_h", "result")
    min_s = cv2.getTrackbarPos("min_s", "result")
    min_v = cv2.getTrackbarPos("min_v", "result")
    max_h = cv2.getTrackbarPos("max_h", "result")
    max_s = cv2.getTrackbarPos("max_s", "result")
    max_v = cv2.getTrackbarPos("max_v", "result")
    dilate_iterations = cv2.getTrackbarPos("dilate", "result")
    erode_iterations = cv2.getTrackbarPos("erode", "result")

    frame_to_tresh = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(frame_to_tresh, (min_h, min_s,
                        min_v), (max_h, max_s, max_v))
    mask = cv2.erode(thresh, None, iterations=erode_iterations)
    mask = cv2.dilate(mask, None, iterations=dilate_iterations)
    contours = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None

    masked_image = cv2.bitwise_and(frame, frame, mask=mask)

    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(max_contour)
        frame_y, frame_x, chan = frame.shape

        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 5)
        cv2.circle(masked_image, (int(x), int(y)), int(radius), (0, 255, 255), 5)

        points.append((int(x), int(y)))

        line = f"x{int(x) - frame_x / 2}y{int(y) - frame_y / 2}\n"
        print(line)

    for i in range (1, len(points)):
        if points[i - 1] is None or points[i] is None:
            continue
        thickness = int(40 / float((20 - i) + 1))    
        cv2.line(frame, points[i - 1], points[i], (0, 0, 255), thickness)
        cv2.line(masked_image, points[i - 1], points[i], (0, 0, 255), thickness)

    left = np.vstack((cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB), frame))
    all = np.hstack((cv2.resize(left, (0, 0), fx=0.5, fy=0.5), masked_image))
    cv2.imshow("result", all)
    cv2.imshow("frame", frame)

    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break