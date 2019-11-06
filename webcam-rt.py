import pyfakewebcam
import cv2
import time
import numpy as np
from datetime import datetime, timedelta
PROCESSING_HEIGHT = 720
PROCESSING_WIDTH = 1280

def run_rt(webcam):
    video_capture = cv2.VideoCapture(2)
    time.sleep(1)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    width = video_capture.get(3)  # float
    height = video_capture.get(4)  # float
    print("webcam dimensions = {} x {}".format(width, height))
    haar_cascade_face = cv2.CascadeClassifier('opencv-data/haarcascade_frontalface_default.xml')

    # video_capture = cv2.VideoCapture('./data/videos/ale.mp4')
    if (webcam):
        # create fake webcam device
        camera = pyfakewebcam.FakeWebcam('/dev/video4', PROCESSING_WIDTH, PROCESSING_HEIGHT)
        camera.print_capabilities()
        print("Fake webcam created")

    # loop until user clicks 'q' to exit
    frame_count = 0
    td = timedelta(seconds=0.1)
    now = datetime.now()
    one_sec = now + td
    next_update_time = [one_sec, one_sec, one_sec, one_sec]
    next_update_val = [0, 0, 0, 0]
    current_viewport = [0, 0, PROCESSING_HEIGHT, PROCESSING_WIDTH]
    first_frame = True
    next_frame = now + timedelta(seconds=1 / 30.0)
    run_face_detection = True
    while True:
        now = datetime.now()
        if now >= next_frame:
            next_frame = now + timedelta(seconds=1/30.0)
            frame_count = (frame_count + 1) % 30
            ret, frame = video_capture.read()
            frame = cv2.resize(frame, (PROCESSING_WIDTH, PROCESSING_HEIGHT))
            current_x, current_y, current_h, current_w = current_viewport
            aim_up = -10
            center_point = [current_x + (current_w/2), current_y + current_h/2 + aim_up]
            output_ratio = PROCESSING_WIDTH/(PROCESSING_HEIGHT*1.0)
            zoomout = 1.4
            crop_height = int(current_h*zoomout)
            crop_width = int(crop_height*output_ratio)
            ideal_crop = [center_point[0] - (crop_width/2), center_point[1] - (crop_height/2)]
            ideal_crop = list(map(int, ideal_crop))
            image = frame[ideal_crop[1]:ideal_crop[1]+crop_height, ideal_crop[0]:ideal_crop[0]+crop_width]
            image = cv2.resize(image, (PROCESSING_WIDTH, PROCESSING_HEIGHT))

            if frame_count == 0:
                run_face_detection = True

            if webcam:
                # firefox needs RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                camera.schedule_frame(image)

            else:
                cv2.imshow('Video', image)

            if run_face_detection:
                faces_rects = haar_cascade_face.detectMultiScale(frame, scaleFactor=3, minNeighbors=5)
                run_face_detection = False
            for i in range(4):
                if next_update_time[i] < now:
                    current_viewport[i] += next_update_val[i]
                    next_update_val[i] = 0
            if len(faces_rects) == 1:
                if first_frame:
                    current_viewport = np.copy(faces_rects[0])
                    first_frame = False
                for i in range(4):
                    diff = current_viewport[i] - faces_rects[0][i]
                    next_update_val[i] = 0
                    if diff > 0:
                        next_update_val[i] = -1
                    if diff < 0:
                        next_update_val[i] = 1
                    if abs(diff) > 20:
                        update_rate = 30
                        if i in [2,3]:  # slow down the zoom of the crop
                            update_rate = 15
                        next_update_time[i] = now + (td / (min(abs(diff), update_rate)))
                    else:
                        next_update_val[i] = 0

if __name__ == "__main__":
    run_rt(True)
