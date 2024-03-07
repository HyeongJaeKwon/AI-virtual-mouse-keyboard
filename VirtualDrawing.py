
import cv2
import time
import mediapipe
import numpy as np
import HandTrackingModule as htm
import os

# getting four images
folderPath = "Header"
myList = os.listdir(folderPath)
overlayList = []
for imPath in myList[1:]:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)


# camera
cap = cv2.VideoCapture(0)
cap.set(3, 1388)
cap.set(4, 1388)
# height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# ----------------------------
header = overlayList[1]
detector = htm.handDetector(detectionCon=0.85)
drawColor = (0, 255, 0)
drawThickness = 15
eraserThickness = 70
xp, yp = 0, 0
imgCanvas = np.zeros((int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                     int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 3), np.uint8)
# ----------------------------

while True:
    # 1. put header image

    success, img = cap.read()
    img = cv2.flip(img, 1)

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # setting the header image
    img[0:header.shape[0], 0:header.shape[1]] = header

    # 2. find hand landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        print(x1, y1)

        # 3. check which finger is up
        fingers = detector.fingersUp()
        # print(fingers)

        # 4. Selection mode - two fingers up
        if fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]:
            # print("Selection mode")
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2+25),
                          drawColor, cv2.FILLED)
            if y1 < header.shape[0]:
                if 200 < x1 < 350:
                    header = overlayList[1]
                    drawColor = (0, 255, 0)
                elif 500 < x1 < 650:
                    header = overlayList[0]
                    drawColor = (255, 0, 0)
                elif 800 < x1 < 950:
                    header = overlayList[3]
                    drawColor = (0, 0, 255)
                elif 1000 < x1 < 1150:
                    header = overlayList[2]
                    drawColor = (0, 0, 0)

        # 5. Drawing mode - Index finger up
        elif fingers[1] and not fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]:
            # print("drawing mode")

            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
            # 1. you can either have collection of points/circles
            # orrrr you can have lines that connects all the points
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            # draw on canvas
            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1),
                         (drawColor), eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, drawThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1),
                         (drawColor), drawThickness)

            xp, yp = x1, y1

        else:
            xp, yp = 0, 0

    # open camera
    cv2.imshow("Image", img)
    # cv2.imshow("Canvas", imgCanvas)
    # Break the loop when the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and destroy any OpenCV windows
cap.release()
cv2.destroyAllWindows()
