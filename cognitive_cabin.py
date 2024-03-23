import base64
import cmd
import json
from time import time

import cv2
import httpx
from ollama import Client
import ollama

from text_to_speech import TextToSpeech
from video_analysis import VideoAnalysis

last_json_instructions = ''

client = Client(host='http://localhost:11434')
text_to_speech = TextToSpeech()

llm_cabin_assistant = "mistral_cabin_assistant"
llm_direction_assistant_extractor = "mistral_direction_assistant_extractor"
llm_picture_descriptor = "llava_picture_descriptor"

llms = [
    llm_cabin_assistant,
    llm_direction_assistant_extractor,
    llm_picture_descriptor
]


def convert_image_to_b64(image):
    success, encoded_image = cv2.imencode('.jpg', image)
    bts = encoded_image.tobytes()
    b64encoded = base64.b64encode(bts)
    return b64encoded.decode('utf-8')


class CognitiveCabin(cmd.Cmd):
    intro = 'Initializing Cognitive Cabin. Type help or ? to list commands.\n'
    prompt = '(cogcab) '

    def __init__(self, start_mode="dev"):
        super().__init__()

        text_to_speech.mode = start_mode
        text_to_speech.synthesize("Welcome aboard the Cognitive Cabin Software. "
                                  "Please make yourself comfortable and enjoy the experience.")

        self.video_analysis_thread = None

        self.video_analysis = VideoAnalysis(device_index=0, window_sec=8)
        self.video_analysis.add_observer(self.process)

    def do_start(self, arg):
        if self.video_analysis.pause_processing is None:
            self.video_analysis_thread = self.video_analysis.run_forever_in_thread()
        elif self.video_analysis.pause_processing is True:
            self.do_resume(arg)

    def do_stop(self, arg):
        self.video_analysis.thread_stop_event.set()
        self.video_analysis_thread = None

    def do_pause(self, arg):
        self.video_analysis.pause_processing = True

    def do_resume(self, arg):
        self.video_analysis.pause_processing = False

    @staticmethod
    def do_dev(arg):
        text_to_speech.mode = 'dev'

    @staticmethod
    def do_prod(arg):
        text_to_speech.mode = 'prod'

    @staticmethod
    def do_exit(arg):
        return True

    @staticmethod
    def do_update(arg):
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

    @staticmethod
    def process(images):
        global last_json_instructions

        try:
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
                    'last_json_instructions': last_json_instructions
                })
            }])
            t3 = time()
            print(f"###################\n{cabin_assistant_response['message']['content']}")
            print(f"llm_cabin_assistant took {(t3 - t2)} seconds")

            json_directive_response = ollama.chat(model=llm_direction_assistant_extractor, messages=[{
                'role': 'user',
                'content': cabin_assistant_response['message']['content']
            }])
            text_to_speech.synthesize(cabin_assistant_response['message']['content'])

            t4 = time()
            print(f"###################\n{json_directive_response['message']['content']}")
            print(f"llm_cabin_assistant took {(t4 - t3)} seconds")
            last_json_instructions = json_directive_response['message']['content']
        except ollama._types.ResponseError as re:
            print(f"Exception caught in cognitive_cabin.process() : {re}")
        except httpx.ConnectError as ce:
            print(f"Exception caught in cognitive_cabin.process() : {ce}")



