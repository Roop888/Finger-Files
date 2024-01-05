import cv2
import mediapipe as mp
from pynput.mouse import Button, Controller
import math
import pyautogui
mouse=Controller()

mp_hands = mp.solutions.hands

mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)

tipIds = [4, 8, 12, 16, 20]
pinch=False

cap=cv2.VideoCapture(0)

width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
(screen_width, screen_height) = pyautogui.size()

def drawHandLandmarks(image, hand_landmarks):
    if hand_landmarks:
        for hand_landmarks in hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)


def countFingers(image, hand_landmarks, handNo=0):
    global pinch
     
    # Get all Landmarks of the FIRST Hand VISIBLE
    if hand_landmarks:
        # Get all Landmarks of the FIRST Hand VISIBLE
        landmarks = hand_landmarks[0].landmark   
        
        # Count Fingers
        fingers = []
        
        for lm_index in tipIds:
            # Get Finger Tip and Bottom y Position Value
            finger_tip_y = landmarks[lm_index].y 
            finger_bottom_y = landmarks[lm_index - 2].y
            
            # Check if ANY FINGER is OPEN or CLOSED
            if lm_index!=4:
                if finger_tip_y < finger_bottom_y:
                    fingers.append(1)
                    # print("FINGER with id ",lm_index," is Open")
              
                if finger_tip_y > finger_bottom_y:
                    fingers.append(0)
                    # print("FINGER with id ",lm_index," is Closed")      
        totalfingers = fingers.count(1)

        #Pinch
        #Draw a line between fingertip and thumbtip
        finger_tip_x=int((landmarks[8].x)*width)
        finger_tip_y=int((landmarks[8].y)*height)
        thumb_tip_x=int((landmarks[4].x)*width)
        thumb_tip_y=int((landmarks[4].y)*height)

        cv2.line(image, (finger_tip_x,finger_tip_y),(thumb_tip_x,thumb_tip_y), (255, 0, 0), 2)

        #Draw a circle on the center of the line between fingertip and thumbtip
        center_x=int((finger_tip_x+thumb_tip_x)/2)
        center_y=int((finger_tip_y+thumb_tip_y)/2)
        cv2.circle(image, (center_x,center_y), 10, (255, 0, 0), -1)

        #Calculate the distance between the fingertip and the thumbtip
        distance=math.sqrt((finger_tip_x-thumb_tip_x)**2+(finger_tip_y-thumb_tip_y)**2)
        print(distance)

        print("computerscreen size",screen_width,screen_height)
        print(mouse.position,center_x,center_y)
        relative_mouse_x=(center_x/width)*screen_width
        relative_mouse_y=(center_y/height)*screen_height
        mouse.position=(relative_mouse_x,relative_mouse_y)


        #Check pinch formation condition
        
        #Move the mouse to the center of the line between fingertip and thumbtip
       
        #Calculate the distance between the fingertip and the thumbtip
        #Set the mouse position on the screen relative to the output window size
        #Check pinch formation condition
        if distance>40:
            if pinch==True:
                pinch=False
                mouse.release(Button.left)   

        if distance<40:
            if pinch==False:
                pinch=True
                mouse.press(Button.left)   
                      


while True:
    success, image = cap.read()
    image = cv2.flip(image, 1)
    results = hands.process(image)
    hand_landmarks = results.multi_hand_landmarks
    drawHandLandmarks(image, hand_landmarks)
    countFingers(image, hand_landmarks)
    cv2.imshow("Media Controller", image)
    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()

