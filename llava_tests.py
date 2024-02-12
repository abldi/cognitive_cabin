import cv2
import numpy as np
import base64
import ollama

IMG_HEIGHT = 480
IMG_WIDTH = 640

GRID_X = 3
GRID_Y = 3

cap = cv2.VideoCapture(0)
images = []

if not cap.isOpened():
    raise IOError("Cannot open webcam")


def create_grid_image(images):
    grid_img = np.zeros((IMG_HEIGHT * GRID_X, IMG_WIDTH * GRID_Y, 3), dtype=np.uint8)

    for i, img in enumerate(images):
        row = i // GRID_X
        col = i % GRID_X
        x = row * IMG_WIDTH
        y = col * IMG_HEIGHT
        grid_img[y:y + IMG_HEIGHT, x:x + IMG_WIDTH] = img
    return grid_img


def send_to_ollama(image):
    success, encoded_image = cv2.imencode('.jpg', image)
    bytes = encoded_image.tobytes()
    b64encoded = base64.b64encode(bytes)
    image_content = b64encoded.decode('utf-8')

    response = ollama.chat(
        model='llava',
        messages=[
        {
            'role': 'user',
            'content': 'What is in the picture',
            'images': [image_content]
        }])
    print(response['message']['content'])

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Cannot read frame")
            break

        images.append(frame)
        if len(images) > GRID_X * GRID_Y:
            images.pop(0)
        else:
            continue

        img_grid = create_grid_image(images)

        cv2.imshow("Live", img_grid)
        k = cv2.waitKey(30)

        if k == ord(' '):
            # dsize = (IMG_WIDTH, IMG_HEIGHT)
            # cv2.resize(img_grid, dsize)
            send_to_ollama(img_grid)
        elif k == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
