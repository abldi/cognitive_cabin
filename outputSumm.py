from langchain_community.llms import ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ttsEleven import TTS


def getSpeech(text):
    model = ollama.Ollama(model="llama2")

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

    outParser = StrOutputParser()
    #Combine the model and the prompt
    chain = prompt1 | model | outParser

    #Launch the prompt and make it into TTS
    textToSpeech = TTS("<API KEY>")
    textToSpeech.toVoice(chain.invoke({"input":text}))