import math
import os
from datetime import datetime, timedelta
from time import sleep

import cv2
from imageio.v3 import imread
import imageio
import numpy as np

save_grid_test_img = True


class VideoAnalysis:
    img_height = 480
    img_width = 640
    grid_repr_window = 9

    _observers = []

    def __init__(self, device_index=None, video_path=None, debug=False, grid_img_nb=9, window_sec=30):
        self.grid_repr_window = window_sec
        self.test_image = None
        self.debug = debug

        if debug:
            self.test_image_contents = []
            for i in range(0, 9):
                self.test_image_contents.append(imread(f"./grid_test/{i}.jpg"))
        elif device_index is not None:
            self.mode = 'camera'
            self.reader = imageio.get_reader('<video0>')
        elif video_path is not None:
            self.mode = 'video'
            self.reader = imageio.get_reader(video_path)
            meta_data = self.reader.get_meta_data()
            self.video_fps = int(meta_data.get('fps'))

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

    def run_forever(self):
        frame_number = 0
        buffering_str = ''
        first_grid_saved = False

        if self.debug:
            while True:
                for observer in self._observers:
                    observer(self.test_image_contents)
                sleep(1)

        for frame in self.reader:
            frame_number = frame_number + 1

            if datetime.now() - self.last_image_timestamp > self.snapshot_capture_interval:
                self.images.append(frame)
                self.last_image_timestamp = datetime.now()
                if len(self.images) > self.grid_img_nb:
                    self.images.pop(0)

            cv2.imshow("Frame", cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                                           (frame.shape[1] // 2, frame.shape[0] // 2)))
            cv2.imshow("Grid", cv2.resize(cv2.cvtColor(self.create_grid_image(), cv2.COLOR_RGB2BGR),
                                          (frame.shape[1] // 2, frame.shape[0] // 2)))
            cv2.waitKey(1)

            if len(self.images) != self.grid_img_nb:
                sleep((1 if self.mode == 'camera' else int(self.video_fps)) / 1000)

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
                    imageio.imwrite(f"{dir_name}/{i}.jpg", img)
                    i = i + 1
                first_grid_saved = True

            for observer in self._observers:
                observer(self.images)
                # observer(self.create_grid_image())
