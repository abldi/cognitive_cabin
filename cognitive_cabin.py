import base64
import cmd
import json
from time import time, sleep

import cv2
import httpx
from ollama import Client
import ollama

import audio_analysis
from audio_analysis import AudioAnalysis
from text_to_speech import TextToSpeech
from video_analysis import VideoAnalysis

last_json_instructions = ''

client = Client(host='http://localhost:11434')
text_to_speech = TextToSpeech()

llm_cabin_assistant = "mistral_cabin_assistant"
llm_direction_assistant_extractor = "mistral_direction_assistant_extractor"
llm_picture_descriptor = "llava_picture_descriptor"

audio_conf_file = 'audio.conf'

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

        self.buffered_transcript = ''
        self.streaming = False
        text_to_speech.mode = start_mode

        self.video_analysis_thread = None
        self.audio_analysis_thread = None

        self.video_analysis = VideoAnalysis(device_index=0, window_sec=8)
        self.video_analysis.add_observer(self.process)

        self.audio_analysis = AudioAnalysis(audio_conf_file)
        self.audio_analysis.add_observer(self.audio_transcript_ready)

    def audio_transcript_ready(self, transcript: str):
        if not self.streaming:
            self.buffered_transcript += transcript + " "

    def audio_stream_finished(self):
        self.streaming = False

    def do_devices(self, arg):
        audio_analysis.list_audio_devices()

    def do_set_device(self, arg):
        with open(audio_conf_file, 'w') as file:
            file.write(arg)

    def do_start(self, arg):
        if self.video_analysis.pause_processing is None:
            self.video_analysis_thread = self.video_analysis.run_forever_in_thread(self)
            self.audio_analysis_thread = self.audio_analysis.run_forever_in_thread()

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

    def process(self, images):
        global last_json_instructions

        if self.streaming:
            return False

        self.streaming = True

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

            copied_transcript = self.buffered_transcript
            self.buffered_transcript = ''
            print({
                    'cabin scene description': picture_description['message']['content'],
                    'passenger transcript': copied_transcript
                })
            cabin_assistant_response = ollama.chat(model=llm_cabin_assistant, messages=[{
                'role': 'user',
                'content': json.dumps({
                    'cabin scene description': picture_description['message']['content'],
                    'passenger transcript': copied_transcript
                })
            }])
            t3 = time()
            print(f"###################\n{cabin_assistant_response['message']['content']}")
            print(f"llm_cabin_assistant took {(t3 - t2)} seconds")

            self.streaming = True
            text_to_speech.synthesize(cabin_assistant_response['message']['content'],
                                      stream_end_callback=self.audio_stream_finished)
        except ollama._types.ResponseError as re:
            print(f"Exception caught in cognitive_cabin.process() : {re}")
        except httpx.ConnectError as ce:
            print(f"Exception caught in cognitive_cabin.process() : {ce}")
        return True



