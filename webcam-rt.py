import pyfakewebcam
import cv2
import time
import numpy as np
from datetime import datetime, timedelta
CAPTURE_WIDTH = 1920
CAPTURE_HEIGHT = 1080
PROCESSING_HEIGHT = 720
PROCESSING_WIDTH = 1280
AXIS_LIMITS = [
    [[0], [PROCESSING_HEIGHT]],
    [[0], [PROCESSING_WIDTH]]
]
AXIS_MIN = 0
AXIS_MAX = 1
X = 0
Y = 1
HEIGHT = 2
WIDTH = 3
FPS = 30
def run_rt(webcam):
    video_capture = cv2.VideoCapture(0)
    time.sleep(1)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

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
    td = timedelta(seconds=1)
    now = datetime.now()
    one_sec = now + td
    next_update_time = [one_sec, one_sec, one_sec, one_sec]
    time_until_next_crop = [td, td, td, td]
    next_update_val = [0, 0, 0, 0]
    current_viewport = [0, 0, PROCESSING_HEIGHT, PROCESSING_WIDTH]
    first_frame = True
    next_frame = now + timedelta(seconds=1.0/FPS)
    run_face_detection = True
    faces_rects = []
    output_ratio = PROCESSING_WIDTH/(PROCESSING_HEIGHT*1.0)
    while True:
        now = datetime.now()
        if now >= next_frame:
            ''' PERFORM CROP '''
            try:
                next_frame = now + timedelta(seconds=1.0/FPS)
                frame_count = (frame_count + 1) % FPS
                ret, frame = video_capture.read()
                frame = cv2.resize(frame, (PROCESSING_WIDTH, PROCESSING_HEIGHT))
                current_x, current_y, current_h, current_w = current_viewport
                aim_up = -10
                center_point = [current_x + (current_w/2), current_y + current_h/2 + aim_up]
                zoomout = 2.0
                crop_height = int(current_h*zoomout)
                crop_width = int(crop_height*output_ratio)
                ideal_crop = [center_point[X] - (crop_width/2), center_point[Y] - (crop_height/2)]
                ideal_crop = list(map(int, ideal_crop))
                '''constrain crop'''
                for i in [X, Y]:
                    if i == X:
                        ideal_crop[i] = max(min(ideal_crop[i], PROCESSING_WIDTH - crop_width), 0)
                    if i == Y:
                        ideal_crop[i] = max(min(ideal_crop[i], PROCESSING_HEIGHT - crop_height), 0)
                image = frame[ideal_crop[Y]:ideal_crop[Y]+crop_height, ideal_crop[X]:ideal_crop[X]+crop_width]
                image = cv2.resize(image, (PROCESSING_WIDTH, PROCESSING_HEIGHT))
            except Exception as e:
                print(e)

            if frame_count == 0:
                run_face_detection = True
            ''' OUTPUT FRAME '''
            if webcam:
                # firefox needs RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                camera.schedule_frame(image)

            else:
                cv2.imshow('Video', image)
            ''' BEGIN FACE DETECTION '''
            if run_face_detection:
                new_faces_rects = haar_cascade_face.detectMultiScale(frame, scaleFactor=2, minNeighbors=5)
                run_face_detection = False
            ''' SCHEDULE CROP AND PAN '''
            if len(new_faces_rects) == 1:
                faces_rects = new_faces_rects
                if first_frame:
                    current_viewport = np.copy(faces_rects[0])
                    first_frame = False
                for i in [X, Y, HEIGHT]: # WIDTH is excluded because we don't even care, we just derive it from the height
                    diff = current_viewport[i] - faces_rects[0][i]
                    next_update_val[i] = 0
                    if diff > 0:
                        next_update_val[i] = -1
                    if diff < 0:
                        next_update_val[i] = 1
                    if (i in [X, Y] and abs(diff) > 20) or (i in [HEIGHT] and abs(diff) > 10):
                        update_rate = FPS*10
                        if i in [HEIGHT]:  # slow down the zoom of the crop
                            update_rate = 15
                        time_until_crop = (td / min(abs(diff), update_rate))
                        time_until_next_crop[i] = time_until_crop
                        next_update_time[i] = now
                    else:
                        next_update_val[i] = 0
        ''' SET CROP AND PAN '''
        lowest_time = timedelta(seconds=1)
        for i in [X, Y , HEIGHT]: # ignore width, it is derived from height.
            if next_update_time[i] <= now:
                current_viewport[i] += next_update_val[i]
                if i == HEIGHT: # if height
                    current_viewport[WIDTH] = int(current_viewport[i]/output_ratio)
                if len(faces_rects) and current_viewport[i] == faces_rects[0][i]:
                    next_update_val[i] = 0
                next_update_time[i] = now + time_until_next_crop[i]
                if time_until_next_crop[i] < lowest_time:
                    lowest_time = time_until_next_crop[i]
        frame_time = datetime.now() - now
        next_frame_min = max((timedelta(seconds=1.0/FPS) - frame_time).total_seconds(), 0)
        next_frame_sched = max((lowest_time - frame_time).total_seconds(), 0)
        sleep_time = min(next_frame_sched, next_frame_min)
        if (sleep_time > 0):
            time.sleep(sleep_time)


if __name__ == "__main__":
    run_rt(True)
