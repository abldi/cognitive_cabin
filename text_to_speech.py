from elevenlabs import generate, play, stream, voices
from elevenlabs.client import ElevenLabs
import time

from langchain_community.llms.ollama import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class TextToSpeech:
    def __init__(self, api_key='your_api_key') -> None:
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)

    def summarize(self, text: str, model="llama2"):
        llm = Ollama(model=model)

        prompt1 = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an AI assistant component whose function is to summarize a prompt into a short message to be said out loud.
                This message aims to be the most similar to human expression, has to summarize all the critical information without repetitions in short sentences and 
                express them with a respectful and helpful tone to the user.
                You are an expert in receiving an input which contains lots of information and summarizing it in short phrases.
                Each phrase talk about a configuration aspect of the car or give some information asked.
                The configuration aspects you control and take in consideration for the phrases are 
                temperature setting, seating inclination, volume setting, window position, lighting level setting, scent setting and music type selection.
                Apart from those settings, you must also consider in the summary the information requested directly by the user and the response for that request.
                This summary must not contain introducing phrases or conclusion expressions, you only produce short phrases for each critical point of information on the text 
                that you are summarizing."""),
                ("user","Text to summarize: {input}")
            ]
        )

        output_parser = StrOutputParser()
        chain = prompt1 | llm | output_parser

        return chain.invoke({"input": text})

    def synthesize(self, text, voice="Lily", use_stream=False, model="eleven_turbo_v2"):
        beginning = time.time()

        if not use_stream:
            audio = generate(
                api_key=self.api_key,
                text=text,
                voice=voice,
                model=model
            )
            end = time.time()
            print(f"\n Model {model} latency is {str(end - beginning)} seconds")
            play(audio)
        else:
            audio = generate(
                api_key=self.api_key,
                text=text,
                voice=voice,
                model=model,
                stream=True,
            )
            end = time.time()
            print(f"\n Model {model} latency is {str(end - beginning)} seconds")
            stream(audio)

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
