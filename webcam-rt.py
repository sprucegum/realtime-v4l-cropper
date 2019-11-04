import pyfakewebcam
import cv2
import time
import numpy as np
from datetime import datetime, timedelta


def run_rt(webcam):
    video_capture = cv2.VideoCapture(2)
    time.sleep(1)

    width = video_capture.get(3)  # float
    height = video_capture.get(4) # float
    print("webcam dimensions = {} x {}".format(width,height))
    haar_cascade_face = cv2.CascadeClassifier('opencv-data/haarcascade_frontalface_default.xml')


    #video_capture = cv2.VideoCapture('./data/videos/ale.mp4')
    if (webcam):
        # create fake webcam device
        camera = pyfakewebcam.FakeWebcam('/dev/video4', 640, 360)
        camera.print_capabilities()
        print("Fake webcam created, try using appear.in on Firefox or  ")

    # loop until user clicks 'q' to exit

    current_h = 10
    current_w = 10
    current_y = 10
    current_x = 10
    extra_width = 50
    extra_height = 70
    ew2 = int(extra_width/2)
    eh2 = int(extra_height/2)
    frame_count = 0
    td = timedelta(seconds = 0.1)
    now = datetime.now()
    one_sec = now + td
    next_update_time = [one_sec, one_sec, one_sec, one_sec]
    next_update_val = [0, 0, 0, 0]
    current_viewport = [0,0,0,0]
    first_frame = True
    next_frame = now + timedelta(seconds = 1/30.0)
    while True:
        now = datetime.now()
        if (now > next_frame):
            next_frame = now + timedelta(seconds = 1/30.0)
            frame_count = (frame_count + 1) % 30
            ret, frame = video_capture.read()
            frame = cv2.resize(frame, (640, 360))
            # flip image, because webcam inverts it and we trained the model the other way!
            frame = cv2.flip(frame,1)
            image = frame
            # flip it back
            image = cv2.flip(image,1)
            try:
                faces_rects = haar_cascade_face.detectMultiScale(image, scaleFactor = 1.2, minNeighbors = 5)
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
                        if diff > 5:
                            next_update_val[i] = -1
                        if diff < -5:
                            next_update_val[i] = 1
                        if abs(diff) > 5:
                            next_update_time[i] = now + (td/(max(abs(diff), 60)))

                current_x, current_y, current_h, current_w = current_viewport
                image = image[current_y-eh2:current_y+current_h+eh2, current_x-ew2:current_x+current_w+ew2]
                image_height = current_h + extra_height
                image_width = current_w + extra_width
                #scale_ratio = image_width/(image_height*1.0)
                target_width = int((360.0/image_height)*image_width)
                image = cv2.resize(image, (target_width, 360))
                blank_image = np.zeros((360, 640, 3), np.uint8)
                paste_position = int((640/2) - image_width/2)
                blank_image[0:360, paste_position:paste_position + target_width] = image
                image = blank_image
                #image = cv2.resize(image, (640, 360))
                #print(faces_rects)


                if (webcam):
                    # firefox needs RGB

                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    # chrome and skype UYUV - not working at the

                    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    # chrome and skype UYUV - not working at the moment

                    # image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)

                    camera.schedule_frame(image)
                    #print("writing to stream")

                else:
                    cv2.imshow('Video', image)
                    #print("writing to screen")
            except Exception as e:
                print(e)
                pass

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                video_capture.release()
                break

if __name__ == "__main__":
    run_rt(True)
