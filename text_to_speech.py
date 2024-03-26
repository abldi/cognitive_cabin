import os
import tempfile
import requests

from elevenlabs import generate, play, stream, voices
from elevenlabs.client import ElevenLabs
from TTS.api import TTS
import torch
from gtts import gTTS


class TextToSpeech:
    mode = 'dev'

    voices = ['Nicole', 'Dave', 'Dorothy', 'Thomas']
    current_voice_index = 0

    def __init__(self) -> None:
        self.api_key = 'b75619b87fb87caf47e18639e4cf4098'  # os.getenv('ELEVENLABS_API_KEY')
        self.client = ElevenLabs(api_key=self.api_key)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # print(TTS().list_models())
        # self.tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False).to(self.device)
        # self.tts.tts_to_file(text="Ich bin eine Testnachricht.", file_path='./test.wav')

    def display_elevenlabs_usage(self):
        sub = self.client.user.get_subscription()
        print(f"Current ElevenLabs subscription is used at {int(sub.character_count * 100 / sub.character_limit)}% "
              f"[{sub.character_count}/{sub.character_limit} characters]")

    def synthesize(self, text, model="eleven_turbo_v2", stream_end_callback=lambda: None):
        if self.mode != 'prod':
            tts = gTTS(text, lang='en')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                temp_filename = fp.name

            os.system(f'mpg123 -q {temp_filename}')
            os.remove(temp_filename)
        else:
            voice = self.voices[self.current_voice_index]
            self.current_voice_index = (self.current_voice_index + 1) % len(self.voices)

            audio = generate(
                api_key=self.api_key,
                text=text,
                voice=voice,
                model=model,
                stream=True,
            )
            stream(audio)
        if stream_end_callback is not None:
            stream_end_callback()

    @staticmethod
    def get_voices():
        voices_list = voices()

        print("Available Voices:")
        for voice in voices_list:
            print(voice.name, end=', ')

    def get_models(self):
        models = self.client.models.get_all()

        print("Available Models:")
        for model in models:
            print(model.model_id, end=', ')
