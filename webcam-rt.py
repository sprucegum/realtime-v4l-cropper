import pyfakewebcam
import cv2
import time
import numpy as np
from datetime import datetime, timedelta
OUTPUT_WIDTH = 640
OUTPUT_HEIGHT = 360

def run_rt(webcam):
    video_capture = cv2.VideoCapture(2)
    time.sleep(1)

    width = video_capture.get(3)  # float
    height = video_capture.get(4)  # float
    print("webcam dimensions = {} x {}".format(width, height))
    haar_cascade_face = cv2.CascadeClassifier('opencv-data/haarcascade_frontalface_default.xml')

    # video_capture = cv2.VideoCapture('./data/videos/ale.mp4')
    if (webcam):
        # create fake webcam device
        camera = pyfakewebcam.FakeWebcam('/dev/video4', OUTPUT_WIDTH, OUTPUT_HEIGHT)
        camera.print_capabilities()
        print("Fake webcam created, try using appear.in on Firefox or  ")

    # loop until user clicks 'q' to exit

    extra_height = 70
    extra_width = 50
    ew2 = int(extra_width / 2)
    eh2 = int(extra_height / 2)
    frame_count = 0
    td = timedelta(seconds=0.1)
    now = datetime.now()
    one_sec = now + td
    next_update_time = [one_sec, one_sec, one_sec, one_sec]
    next_update_val = [0, 0, 0, 0]
    cv_width = 640
    cv_height = 360
    current_viewport = [ew2, eh2, cv_height - extra_height, cv_width - extra_width]
    first_frame = True
    fps = 30.0
    next_frame = now + timedelta(seconds=1 / fps)
    run_face_detection = True
    ret, frame = video_capture.read()
    input_width = 1920
    input_height = 1080

    input_to_cv_ratio = (input_width*1.0)/cv_width
    while True:
        now = datetime.now()
        if now >= next_frame:
            next_frame = now + timedelta(seconds=1/fps)
            frame_count = (frame_count + 1) % fps
            ret, frame = video_capture.read()
            image = frame
            try:
                current_x, current_y, current_h, current_w = current_viewport
                image = image[current_y - eh2:current_y + current_h + eh2, current_x - ew2:current_x + current_w + ew2]
                image_height = current_h + extra_height
                image_width = (current_w + extra_width)*1.0
                target_width = int((cv_height*1.0 / image_height) * image_width)
                image = cv2.resize(image, (target_width, cv_height))
                blank_image = np.zeros((cv_height, cv_width, 3), np.uint8)
                paste_position = int((cv_width / 2) - image_width / 2)
                blank_image[0:cv_height, paste_position:paste_position + target_width] = image
                image = blank_image
                run_face_detection = True
                if (webcam):
                    # OBS needs RGB
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    camera.schedule_frame(image)

                else:
                    cv2.imshow('Video', image)

            except Exception as e:
                print(e, target_width)
                pass

            # Hit 'q' on the keyboard to quit!
        if run_face_detection:
            faces_rects = haar_cascade_face.detectMultiScale(image, scaleFactor=1.2, minNeighbors=5)
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
                    if diff > 10:
                        next_update_val[i] = -1
                    if diff < -10:
                        next_update_val[i] = 1
                    if abs(diff) > 25:
                        update_rate = 30
                        if i in [2,3]:  # slow down the zoom of the crop
                            update_rate = 2
                        next_update_time[i] = now + (td / (min(abs(diff), update_rate)))


if __name__ == "__main__":
    run_rt(True)
