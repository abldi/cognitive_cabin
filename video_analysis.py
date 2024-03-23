import math
import os
import threading
from datetime import datetime, timedelta
from time import sleep

import cv2
import numpy as np

save_grid_test_img = True


class VideoAnalysis:
    img_height = 480
    img_width = 640
    grid_repr_window = 9

    _observers = []

    def __init__(self, device_index=None, video_path=None, debug=False, grid_img_nb=9, window_sec=30):
        self.cabin = None
        self.show = True
        self.pause_processing = None
        self.grid_repr_window = window_sec
        self.test_image = None
        self.debug = debug
        self.observer_threads = {}
        self.thread_stop_event = threading.Event()

        if debug:
            self.test_image_contents = []
            for i in range(0, 9):
                self.test_image_contents.append(cv2.imread(f"./grid_test/{i}.jpg"))
        elif device_index is not None:
            self.mode = 'camera'
            self.reader = cv2.VideoCapture(device_index)
        elif video_path is not None:
            self.mode = 'video'
            self.reader = cv2.VideoCapture(video_path)
            self.video_fps = self.reader.get(cv2.CAP_PROP_FPS)

        self.images = []

        self.last_image_timestamp = datetime.now() - timedelta(seconds=window_sec)
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

    def run_forever_in_thread(self, cognitive_cabin):
        self.cabin = cognitive_cabin
        thread = threading.Thread(target=self.run_forever)
        thread.start()

        return thread

    def run_forever(self):
        frame_number = 0
        buffering_str = ''
        first_grid_saved = False

        if self.debug:
            while True:
                for observer in self._observers:
                    observer(self.test_image_contents)
                sleep(1)

        while not self.thread_stop_event.is_set():
            if self.pause_processing:
                sleep(1)
                continue

            ret, frame = self.reader.read()
            if not ret:
                print("Error while reading - end of stream ?")
                break

            frame_number = frame_number + 1

            if (datetime.now() - self.last_image_timestamp > self.snapshot_capture_interval or
                    len(self.images) < self.grid_img_nb):
                self.images.append(frame)
                self.last_image_timestamp = datetime.now()
                if len(self.images) > self.grid_img_nb:
                    self.images.pop(0)

            if len(self.images) != self.grid_img_nb:
                sleep(1 / 1000)

                tmp_str = f"{len(self.images)}/{self.grid_img_nb} images in buffer ..."
                if buffering_str != tmp_str:
                    buffering_str = tmp_str
                    print(buffering_str)
                continue

            if not first_grid_saved and save_grid_test_img:
                dir_name = './grid_test'
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                i = 0
                for img in self.images:
                    cv2.imwrite(f"{dir_name}/{i}.jpg", img)
                    i = i + 1
                first_grid_saved = True

            for observer in self._observers:
                if (not self.cabin.streaming and
                        (observer not in self.observer_threads or not self.observer_threads[observer].is_alive())):
                    thread = threading.Thread(target=observer, args=(self.images,))
                    thread.start()

                    self.observer_threads[observer] = thread