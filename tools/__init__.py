import numpy as np
import cv2


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
        