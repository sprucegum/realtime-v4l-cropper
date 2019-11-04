import pyfakewebcam
import cv2
import time
import numpy as np



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
    last_h = 0
    last_w = 0
    last_y = 0
    last_x = 0
    current_h = 10
    current_w = 10
    current_y = 10
    current_x = 10
    extra_width = 50
    extra_height = 70
    ew2 = int(extra_width/2)
    eh2 = int(extra_height/2)
    frame_count = 0
    while True:
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
            if len(faces_rects) == 1:
                h = faces_rects[0][2]
                w = faces_rects[0][3]
                y = faces_rects[0][1]
                x = faces_rects[0][0]
                if (frame_count == 0):
                    current_h += int((h - last_h)/2)
                    current_w += int((w - last_w)/2)
                    current_y += int((y - last_y)/2)
                    current_x += int((x - last_x)/2)
                #print(current_h, current_w, current_y, current_x)
                last_h = current_h
                last_w = current_w
                last_y = current_y
                last_x = current_x
            image = image[current_y-eh2:current_y+current_h+eh2, current_x-ew2:current_x+current_w+ew2]
            blank_image = np.zeros((360, 640, 3), np.uint8)
            blank_image[0:current_h+extra_height, 0:current_w+extra_width] = image
            image = blank_image
            #image = cv2.resize(image, (640, 360))
            #print(faces_rects)
        except:
            pass

        if (webcam):
            time.sleep(1/30.0)
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

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            break

if __name__ == "__main__":
    run_rt(True)
