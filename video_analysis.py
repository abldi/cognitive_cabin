from datetime import datetime, timedelta

import cv2
import numpy as np
import base64
import ollama


def send_to_ollama(image_array):
    print(f"Sending {len(image_array)} images to ollama")

    try:
        image_content_array = []

        for image in image_array:
            success, encoded_image = cv2.imencode('.jpg', image)
            bytes = encoded_image.tobytes()
            b64encoded = base64.b64encode(bytes)
            image_content = b64encoded.decode('utf-8')
            image_content_array.append(image_content)

        response = ollama.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': 'Describe whats happening in the pictures.',
                'images': image_content_array
            }])
        print(response['message']['content'])
    except Exception as e:
        print(e)


class VideoAnalysis:
    img_height = 480
    img_width = 640
    grid_size = (3, 3)
    grid_repr_window = 9

    def __init__(self, device_index=None, video_path=None):
        if device_index is not None:
            self.mode = 'camera'
            self.cap = cv2.VideoCapture(0)
        elif video_path is not None:
            self.mode = 'video'
            self.cap = cv2.VideoCapture(video_path)
            self.video_total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.grid_repr_window = self.video_total_frames / self.video_fps
            self.img_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.img_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.grid_img = None
        self.images = []

        self.grid_img_nb = self.grid_size[0] * self.grid_size[1]
        self.last_image_timestamp = datetime.now()
        self.snapshot_capture_interval = timedelta(seconds=self.grid_repr_window / self.grid_img_nb)

        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    def create_grid_image(self):
        grid_img = np.zeros((self.img_height * self.grid_size[0], self.img_width * self.grid_size[1], 3),
                            dtype=np.uint8)

        for i, img in enumerate(self.images):
            row = i % self.grid_size[0]
            col = i // self.grid_size[0]
            x = row * self.img_width
            y = col * self.img_height
            grid_img[y:y + self.img_height, x:x + self.img_width] = img
        return grid_img

    def run_forever(self):
        frame_number = 0

        try:
            while True:
                ret, frame = self.cap.read()

                if not ret:
                    if self.mode == 'camera':
                        print("Cannot read frame")
                    break

                frame_number = frame_number + 1

                if self.mode == 'camera':
                    if datetime.now() - self.last_image_timestamp > self.snapshot_capture_interval:
                        self.images.append(frame)
                        self.last_image_timestamp = datetime.now()
                        if len(self.images) > self.grid_img_nb:
                            self.images.pop(0)

                    cv2.imshow("Live Current", cv2.resize(frame, (800, 600)))
                    k = cv2.waitKey(1)

                    if k == ord(' '):
                        cv2.imshow("Grid (camera)", cv2.resize(self.create_grid_image(), (800, 600)))
                        send_to_ollama(self.images)

                elif self.mode == 'video':
                    if frame_number % (self.video_total_frames // self.grid_img_nb) == 0:
                        self.images.append(frame)
                        cv2.imshow("Grid (video)", cv2.resize(self.create_grid_image(), (800, 600)))
                        cv2.waitKey(1)
                        if len(self.images) == self.grid_img_nb:
                            send_to_ollama(self.images)
        finally:

            self.cap.release()
            cv2.destroyAllWindows()
