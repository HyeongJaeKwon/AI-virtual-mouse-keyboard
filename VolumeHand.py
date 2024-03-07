
import cv2
import time
import mediapipe
import numpy as np
import HandTrackingModule as htm
import math
import osascript


############################
wCam, hCam = 640, 480
pTime = 0
cTime = 0
detector = htm.handDetector(detectionCon=0.7)
volBar = 400
vol = 0
############################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)


# n = 100
# osascript.osascript(f"set volume output volume {n}")

while True:
    success, img = cap.read()

    # detect hand
    img = detector.findHands(img)

    # get landmark list
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) > 0:
        # print(lmList[4], lmList[8])

        # circles on two fingers + center + line
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(img, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        length = math.hypot(x2-x1, y2-y1)
        if length < 25:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        # adjust volume
        vol = np.interp(length, [25, 300], [0, 100])
        volBar = np.interp(length, [25, 300], [400, 150])
        # print(int(length), vol)
        osascript.osascript(f"set volume output volume {vol}")

    cv2.putText(img, f"Vol: {int(vol)}%", (35, 450),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

    # frame no.
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # open camera
    cv2.imshow("Image", img)
    # Break the loop when the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and destroy any OpenCV windows
cap.release()
cv2.destroyAllWindows()
