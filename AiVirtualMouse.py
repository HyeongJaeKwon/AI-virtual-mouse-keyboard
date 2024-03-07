import cv2
import time
import numpy
import pyautogui
import HandTrackingModule as htm

####################
wCap, hCap = 680, 680
detector = htm.handDetector(detectionCon=0.8)
px, py = 0, 0
moving = False
pTime = 0
smoothening = 1.4
dragSmooth = 0.8
keys = [["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
        ["backspace", "space", "enter"]]


showKeyboard = False
####################
####################

# draw keyboard


def drawAll(img, buttonList):
    mask = img.copy()

    # draw keys
    for button in buttonList:
        bt = button.text
        if bt == "backspace":
            bt = "<"
        elif bt == "space":
            bt = " "
        elif bt == "enter":
            bt = ">"
        cv2.rectangle(mask, button.pos, (button.pos[0]+button.size[0], button.pos[1]+button.size[1]),
                      (255, 0, 255), cv2.FILLED)
        cv2.putText(mask, bt, (button.pos[0]+25, button.pos[1]+60), cv2.FONT_HERSHEY_COMPLEX,
                    2, (255, 255, 255), 5)
        # Adjust transparency here (0 = fully transparent, 1 = opaque)
        alpha = 0.2
        masked_img = cv2.addWeighted(img, 1 - alpha, mask, alpha, 0)

    # draw keyboard toggle
    cv2.rectangle(masked_img, (50, 400), (400, 500),
                  (175, 0, 175), cv2.FILLED)
    cv2.putText(masked_img, "Keyboard", (60, 470), cv2.FONT_HERSHEY_COMPLEX,
                2, (255, 255, 255), 5)
    # masked_img = cv2.addWeighted(img, 0, mask, 1, 0)

    return masked_img


class Button():
    def __init__(self, pos, text, size=[100, 100]):
        self.pos = pos
        self.size = size
        self.text = text


cap = cv2.VideoCapture(0)
cap.set(3, wCap)
cap.set(4, hCap)


# button list
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([120 * j + 50, 120 * i + 500], key))


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if showKeyboard:
        img = drawAll(img, buttonList=buttonList)
    else:
        mask = img.copy()
        cv2.rectangle(mask, (50, 400), (400, 500),
                      (175, 0, 175), cv2.FILLED)
        cv2.putText(mask, "Keyboard", (60, 470), cv2.FONT_HERSHEY_COMPLEX,
                    2, (255, 255, 255), 5)
        img = cv2.addWeighted(img, 1 - 0.2, mask, 0.2, 0)

    # # show text typed
    # cv2.rectangle(img, (50, 400), (700, 500),
    #               (175, 0, 175), cv2.FILLED)
    # cv2.putText(img, finalText, (60, 425), cv2.FONT_HERSHEY_COMPLEX,
    #             2, (255, 255, 255), 5)

    # 1. find hand
    img = detector.findHands(img)

    # 2. find fingers
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        fingers = detector.fingersUp()
        length = detector.findDistance(8, 4)

        # detect which key finger is on
        if showKeyboard:

            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                if x < x1 < x+w and y < y1 < y + h:
                    bt = button.text
                    if bt == "backspace":
                        bt = "<"
                    elif bt == "space":
                        bt = " "
                    elif bt == "enter":
                        bt = ">"
                    cv2.rectangle(img, button.pos, (button.pos[0]+button.size[0], button.pos[1]+button.size[1]),
                                  (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, bt, (button.pos[0]+25, button.pos[1]+60), cv2.FONT_HERSHEY_COMPLEX,
                                2, (255, 255, 255), 5)

                    if length < 50:
                        cv2.rectangle(img, button.pos, (button.pos[0]+button.size[0], button.pos[1]+button.size[1]),
                                      (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, bt, (button.pos[0]+25, button.pos[1]+60), cv2.FONT_HERSHEY_COMPLEX,
                                    2, (255, 255, 255), 5)
                        # finalText += button.text
                        pyautogui.press(button.text)
                        time.sleep(0.35)

         # when clicked keyboard
        if length < 40 and 50 < x1 < 400 and 400 < y1 < 500:
            showKeyboard = not showKeyboard
            time.sleep(0.35)

        # moving mouse
        if fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
            if not moving:
                px, py = x1, y1
                compx, compy = pyautogui.position()
            moving = True
            if moving:
                showKeyboard = False
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                qq, ww = (x1-px)/smoothening, (y1-py)/smoothening
                # print(qq, ww)
                pyautogui.moveTo(compx + qq, compy + ww)

        # click
        elif not fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
            pyautogui.click()

        # doubleclick but doesnt work so it switched to drag
        elif fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            # pyautogui.doubleClick()
            # print("double")
            if not moving:
                px, py = x1, y1
                compx, compy = pyautogui.position()
            moving = True
            if moving:
                showKeyboard = False
                cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 15, (0, 0, 255), cv2.FILLED)
                qq, ww = (x1-px)/dragSmooth, (y1-py)/dragSmooth
                # print(qq, ww)
                pyautogui.dragTo(compx + qq, compy + ww, button="left")
        else:
            moving = False

    # frame number
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70),
                cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 255), 3)
    # show camera
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
