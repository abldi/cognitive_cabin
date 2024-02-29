from ttsEleven import TTS
APIKEY="<Your API key>"
TEXT="This is the output example text to see if the selected voice is appropiate to the purposes we look for"

ttsHandler = TTS(APIKEY)

#Output with default voice
ttsHandler.toVoice(TEXT)

#Get available voices
ttsHandler.getVoices()
#Select a determined voice
ttsHandler.toVoice(TEXT,voiceName="Adam")

#Get other available models
ttsHandler.getModels()
#Select another model
ttsHandler.toVoice(TEXT,modelId="eleven_multilingual_v2")