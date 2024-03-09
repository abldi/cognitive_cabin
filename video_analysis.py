import os.path

import matplotlib.pyplot as plt
from skimage.transform import resize
import math
from datetime import datetime, timedelta
from time import sleep

import imageio
import numpy as np

first_grid_file_path = 'test_stuff/grid_test.jpg'


class VideoAnalysis:
    img_height = 480
    img_width = 640
    grid_repr_window = 9

    _observers = []

    def __init__(self, device_index=None, video_path=None, test_img_path=None, grid_img_nb=9, window_sec=30):
        self.grid_repr_window = window_sec
        self.test_image = None

        if test_img_path is not None:
            self.test_image = imageio.imread(test_img_path)
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

        if self.test_image is not None:
            while True:
                for observer in self._observers:
                    observer(self.test_image)
                sleep(1)

        for frame in self.reader:
            frame_number = frame_number + 1

            if datetime.now() - self.last_image_timestamp > self.snapshot_capture_interval:
                self.images.append(frame)
                self.last_image_timestamp = datetime.now()
                if len(self.images) > self.grid_img_nb:
                    self.images.pop(0)

            if len(self.images) != self.grid_img_nb:
                sleep((1 if self.mode == 'camera' else int(self.video_fps)) / 1000)

                tmp_str = f"{len(self.images)}/{self.grid_img_nb} images in buffer ..."
                if buffering_str != tmp_str:
                    buffering_str = tmp_str
                    print(buffering_str)
                continue

            if not first_grid_saved:
                imageio.imwrite(first_grid_file_path, self.create_grid_image())

            plt.imshow(frame)
            plt.axis('off')
            plt.show(block=False)

            if self.mode == 'camera':
                sleep(self.video_fps / 1000)
            elif self.mode == 'video':
                sleep(self.video_fps / 1000)

            for observer in self._observers:
                observer(self.create_grid_image())
