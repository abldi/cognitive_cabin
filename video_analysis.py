import math
from datetime import datetime, timedelta
from time import sleep

import cv2
import numpy as np
import base64
import ollama


def send_to_llm(image_array):
    try:
        image_content_array = []

        for image in image_array:
            success, encoded_image = cv2.imencode('.jpg', image)
            image_bytes = encoded_image.tobytes()
            b64encoded = base64.b64encode(image_bytes)
            image_content = b64encoded.decode('utf-8')
            image_content_array.append(image_content)

        send_time = datetime.now()
        response = ollama.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': 'Describe the picture.',
                'images': image_content_array
            }])
        print(f"\n--------------------\n"
              f"Took {(datetime.now() - send_time).total_seconds()} seconds")
        print("R1:" + response['message']['content'])

        cabin_prompt = ("As your in-car AI assistant, you're equipped with the ability to autonomously manage the "
                        "needs of all passengers, drawing on real-time and historical data to anticipate those needs "
                        "and decide on the best actions. "
                        "Your capabilities include : "
                        "- adjusting the HVAC system (temperature from 16°C to 34°C and airflow level 1-5), "
                        "- setting the seating recline (1-10 scale), "
                        "- controlling audio volume (0-10 scale), "
                        "- positioning the windows (open, mid, close), "
                        "- customizing cabin lighting (RGB color and intensity level 1-10), "
                        "- selecting cabin scent (Citrus, Woody, Flowery), "
                        "- suggesting music preferences (genre and artist). "
                        "Your main objective is to enhance passenger comfort and safety by smartly coordinating these "
                        "features. "
                        "For example, if a child is sleeping in the back seat, you might lower the temperature to "
                        "improve sleep quality, set the volume to 3, close the windows, emit a woody scent, "
                        "and play soothing classical music. "
                        "Your responses will always start by recognizing the current situation (e.g., 'I see that you "
                        "are sleeping..') followed by your recommendation, communicated in a concise, clear, and "
                        "friendly tone. You adapt your communication style based on the passenger\'s profile, like "
                        "adopting a more playful tone with children. You operate without needing direct commands from "
                        "users, aiming to meet the needs of multiple passengers at once. In the event of conflicting "
                        "needs, you\'ll devise and explain an appropriate compromise."
                        "\n\n"
                        "Here is a description of the current scene, viewed from a realtime camera : ")

        content2 = cabin_prompt + ' ' + response['message']['content']
        response2 = ollama.chat(
            model='mistral',
            messages=[{
                'role': 'user',
                'content': content2
            }])
        print("R2:" + response2['message']['content'])
    except Exception as e:
        print(e)


class VideoAnalysis:
    img_height = 480
    img_width = 640
    grid_repr_window = 9

    def __init__(self, device_index=None, video_path=None, width=640, grid_img_nb=9, window_sec=30):
        self.img_width = width
        self.grid_repr_window = window_sec

        if device_index is not None:
            self.mode = 'camera'
            self.cap = cv2.VideoCapture(device_index)
        elif video_path is not None:
            self.mode = 'video'
            self.cap = cv2.VideoCapture(video_path)
            self.video_total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
            if not self.cap.isOpened():
                print("Error: Unable to open video source")

        self.images = []

        self.last_image_timestamp = datetime.now()
        self.snapshot_capture_interval = timedelta(seconds=self.grid_repr_window / grid_img_nb)
        self.grid_img_nb = grid_img_nb

    def create_grid_image(self):
        if len(self.images) == 0:
            return None

        sqr_image_len_x = math.ceil(math.sqrt(self.grid_img_nb))
        sqr_image_len_y = math.floor(math.sqrt(self.grid_img_nb))
        grid_size = (sqr_image_len_x, sqr_image_len_y)
        grid_img = np.zeros((self.images[0].shape[0] * grid_size[0],
                            self.images[0].shape[1] * grid_size[1], 3),
                            dtype=np.uint8)

        for i, img in enumerate(self.images):
            row = i % grid_size[0]
            col = i // grid_size[0]
            x = row * self.images[0].shape[1]
            y = col * self.images[0].shape[0]
            grid_img[y:y + img.shape[0], x:x + img.shape[1]] = img
        return grid_img

    def run_forever(self):
        frame_number = 0

        try:
            while True:
                ret, frame = self.cap.read()

                if not ret:
                    print('cannot read frame')
                    break

                frame_number = frame_number + 1
                frame = cv2.resize(frame, (self.img_width, int(self.img_width * frame.shape[0] / frame.shape[1])))

                if datetime.now() - self.last_image_timestamp > self.snapshot_capture_interval:
                    self.images.append(frame)
                    self.last_image_timestamp = datetime.now()
                    if len(self.images) > self.grid_img_nb:
                        self.images.pop(0)

                if len(self.images) != self.grid_img_nb:
                    sleep((1 if self.mode == 'camera' else int(self.video_fps)) / 1000)
                    continue

                cv2.imshow("Live Current", cv2.resize(frame, (1066, 600)))
                cv2.imshow("Grid (camera)", cv2.resize(self.create_grid_image(), (1066, 600)))

                cv2.waitKey(1 if self.mode == 'camera' else int(self.video_fps))

                send_to_llm(self.images)
        finally:
            print(f"Caught some bad fishes ...")
            self.cap.release()
            cv2.destroyAllWindows()
