
import cv2
import mediapipe as mp
import time
import math


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, 1, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:

                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):

        self.lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        fingers = []

        # thumb (landmark 4 = tip of thumb | landmark 3 = one below the tip)
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0]-1][1]:
            # right now is < = RIGHT HAND, BUT LATER, NEED TO CHECK IF IT'S RIGHT HAND OR LEFT
            fingers.append(1)
        else:
            fingers.append(0)

        # the rest of four fingers
        for id in self.tipIds[1:]:
            if self.lmList[id][2] < self.lmList[id-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self, finger1, finger2):
        #  # circles on two fingers + center + line
        x1, y1 = self.lmList[finger1][1], self.lmList[finger1][2]
        x2, y2 = self.lmList[finger2][1], self.lmList[finger2][2]
        # cx, cy = (x1+x2)//2, (y1+y2)//2
        # cv2.circle(img, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        length = math.hypot(x2-x1, y2-y1)
        return length
        # if length < 25:
        #     cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()

        # draw skeleton
        img = detector.findHands(img)

        # get landmark list / draw circle
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            print(lmList[4])

        # show frame no.
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 255), 3)

        # camera on
        cv2.imshow("Image", img)

        # Break the loop when the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and destroy any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
