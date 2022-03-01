import cv2
import cvzone
import numpy as np
FACES_CASCADE = cv2.CascadeClassifier("./tools/faces.xml")


def apply_filter(filter, frame):
    if filter == 'grayscale':
        return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR) # converto in grigio e lo ritorno in BGR

    elif filter == 'blur':
        return cv2.GaussianBlur(frame, (15, 15), 0)

    elif filter == 'invert':
        return cv2.bitwise_not(frame)

    elif filter == "mirror": 
        return np.hstack([frame,cv2.flip(frame,1)]) # incolla 2 frame


def face_mask(frame, overlay_image):
    overlay_image = cv2.imread(overlay_image, cv2.IMREAD_UNCHANGED) # IMREAD_UNCHANGED per consentire la lettura di immagini png trasparenti
    gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACES_CASCADE.detectMultiScale(gray_scale, 1.1, 4)
    for (x, y, w, h) in faces:
        overlay_resize = cv2.resize(overlay_image, (w, h)) 
        frame = cvzone.overlayPNG(frame, overlay_resize, [x,y])
    return frame