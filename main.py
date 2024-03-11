import base64
import json
import sys
from datetime import datetime
from time import time

import cv2
from ollama import Client
import ollama

from text_to_speech import TextToSpeech
from video_analysis import VideoAnalysis

client = Client(host='http://localhost:11434')
text_to_speech = TextToSpeech()

history = []

llm_cabin_assistant = "mistral_cabin_assistant"
llm_direction_assistant_extractor = "mistral_direction_assistant_extractor"
llm_picture_descriptor = "llava_picture_descriptor"

llms = [
    llm_cabin_assistant,
    llm_direction_assistant_extractor,
    llm_picture_descriptor
]


def update_models():
    ollama.pull('llava')
    ollama.pull('mistral')

    for llm in llms:
        try:
            ollama.delete(llm)
        except ollama.ResponseError:
            print(f"warning - no '{llm}' model to delete")
            pass
        with open(f"./model_files/{llm}.modelfile", 'r') as mf:
            ollama.create(llm, modelfile=mf.read())

    ollama_list = ollama.list()
    for model in ollama_list['models']:
        print(model['name'])


def convert_image_to_b64(image):
    success, encoded_image = cv2.imencode('.jpg', image)
    bts = encoded_image.tobytes()
    b64encoded = base64.b64encode(bts)
    return b64encoded.decode('utf-8')


def process(images):
    global history

    t1 = time()
    content = [convert_image_to_b64(img) for img in images]
    picture_description = ollama.chat(model=llm_picture_descriptor, messages=[{
        'role': 'user',
        'content': ' ',
        'images': content
    }])
    t2 = time()
    print(f"###################\n{picture_description['message']['content']}")
    print(f"llm_picture_descriptor took {(t2 - t1)} seconds")

    cabin_assistant_response = ollama.chat(model=llm_cabin_assistant, messages=[{
        'role': 'user',
        'content': json.dumps({
            'current_scene_description': picture_description['message']['content'],
            'history': history
        })
    }])
    t3 = time()
    print(f"###################\n{cabin_assistant_response['message']['content']}")
    print(f"llm_cabin_assistant took {(t3 - t2)} seconds")

    history.append([str(datetime.timestamp(datetime.now())), cabin_assistant_response['message']['content']])
    json_directive_response = ollama.chat(model=llm_direction_assistant_extractor, messages=[{
        'role': 'user',
        'content': cabin_assistant_response['message']['content']
    }])
    t4 = time()
    print(f"###################\n{json_directive_response['message']['content']}")
    print(f"llm_cabin_assistant took {(t4 - t3)} seconds")


if __name__ == '__main__':
    # update_models()

    if len(sys.argv) != 2:
        raise Exception(f"Wrong arguments. Aborting.")

    va = VideoAnalysis(video_path=sys.argv[1])
    # va = VideoAnalysis(debug=True)
    va.add_observer(process)
    va.run_forever()
