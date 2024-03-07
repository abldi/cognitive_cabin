import math
from datetime import datetime, timedelta
from time import sleep, time

import cv2
import numpy as np


class VideoAnalysis:
    img_height = 480
    img_width = 640
    grid_repr_window = 9

    _observers = []

    def __init__(self, device_index=None, video_path=None, test_img_path=None, width=640, grid_img_nb=9, window_sec=30):
        self.img_width = width
        self.grid_repr_window = window_sec
        self.test_image = None

        if test_img_path is not None:
            self.test_image = cv2.imread(test_img_path)
        elif device_index is not None:
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

    def add_observer(self, observer):
        self._observers.append(observer)

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

        if self.test_image is not None:
            while True:
                for observer in self._observers:
                    observer(self.test_image)
                sleep(1)

        while True:
            ret, frame = self.cap.read()

            if not ret:
                print(f"cannot read frame")
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

            # cv2.imwrite(f"sample_{time()}.jpg", self.create_grid_image())

            cv2.imshow("Live Current", cv2.resize(frame, (1066, 600)))
            cv2.imshow("Grid (camera)", cv2.resize(self.create_grid_image(), (1066, 600)))

            cv2.waitKey(1 if self.mode == 'camera' else int(self.video_fps))

            for observer in self._observers:
                observer(self.create_grid_image())
