import cv2
import cvzone


class Filter:

    def apply_filter(self, filter, frame):
        if filter == 'grayscale':
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        elif filter == 'blur':
            return cv2.GaussianBlur(frame, (5, 5), 0)

        elif filter == 'invert':
            return cv2.bitwise_not(frame)

        elif filter == "mirror": 
            frame_flip = cv2.flip(frame,1)
            return np.hstack([frame,frame_flip])

class Mask:
    def __init__(self, faces_cascade):
        self.faces_cascade = cv2.CascadeClassifier(faces_cascade)
       
    def face_mask(self, frame, overlay_image = "./masks/pusheen.png"):
        overlay_image = cv2.imread(overlay_image, cv2.IMREAD_UNCHANGED)
        gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.faces_cascade.detectMultiScale(gray_scale, 1.1, 4)
        for (x, y, w, h) in faces:
            overlay_resize = cv2.resize(overlay_image, (w, h))
            frame = cvzone.overlayPNG(frame, overlay_resize, [x,y])
        return frame

    def glasses(self, frame, overlay_image = "./masks/mlg_glasses.png"):
        overlay_image = cv2.imread(overlay_image, cv2.IMREAD_UNCHANGED)
        gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.faces_cascade.detectMultiScale(gray_scale, 1.1, 4)
        for (x, y, w, h) in faces:
            overlay_resize = cv2.resize(overlay_image, (w, h))
            frame = cvzone.overlayPNG(frame, overlay_resize, [x,y-5])
        return frame
        