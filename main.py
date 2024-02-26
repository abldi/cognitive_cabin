import base64
from datetime import datetime

import cv2
import ollama

from video_analysis import VideoAnalysis


def process(image_array):
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
              f"R1 took {(datetime.now() - send_time).total_seconds()} seconds")
        print("R1:" + response['message']['content'])

        cabin_prompt = "Here is a description of the current scene, viewed from a realtime camera : "

        content2 = cabin_prompt + ' ' + response['message']['content']
        send_time = datetime.now()
        response2 = ollama.chat(
            model='cabin-assistant',
            messages=[{
                'role': 'user',
                'content': content2
            }])
        print(f"\n--------------------\n"
              f"R2 took {(datetime.now() - send_time).total_seconds()} seconds")
        print("R2:" + response2['message']['content'])
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # va = VideoAnalysis(device_index=0, window_sec=3, grid_img_nb=9)
    va = VideoAnalysis(
        video_path='/home/tamaya/Documents/cognitive_cabin/test_stuff/14.02.2024/landscape_video_sample_1.mp4',
        window_sec=15,
        grid_img_nb=4,
        width=200)
    va.add_observer(process)
    va.run_forever()
