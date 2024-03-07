from elevenlabs import generate, play, stream, voices
from elevenlabs.client import ElevenLabs
import time

class TTS:
    def __init__(self,apiKey) -> None:
        self.apikey = apiKey

    def toVoice(self,textInput,voiceName="Lily",streamInput = False, modelId = "eleven_turbo_v2"):
        beginning = time.time()
        if not streamInput: #Default
            audio = generate(
                api_key=self.apikey,
                text=textInput,
                voice=voiceName,
                model=modelId
            )
            end = time.time()
            print(f"\n Model {modelId} latency is {str(end-beginning)} seconds")
            play(audio)
        else:
            audio = generate(
                api_key=self.apikey,
                text=textInput,
                voice=voiceName,
                model=modelId,
                stream=True,
            )
            end = time.time()
            print(f"\n Model {modelId} latency is {str(end-beginning)} seconds")
            stream(audio)
        
        

    def getVoices(self):
        voicesList = voices()
        print("Available Voices:")
        for voice in voicesList:
            print(voice.name,end=', ')
    
    def getModels(self):
        elevenClient = ElevenLabs(api_key=self.apikey)
        models = elevenClient.models.get_all()
        print("Available Models:")
        for model in models:
            print(model.model_id, end=', ')
