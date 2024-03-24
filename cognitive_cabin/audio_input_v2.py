import faster_whisper as fw
import os
import pyaudio
import webrtcvad as vtad
import numpy as np
import io

#Global Constants
SAMPLE_RATE=16000
FRAME_DURATION_MS = 20
CHANNELS=1
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

#Functions
def obtain_audio():
    p = pyaudio.PyAudio() #Initialize pyaudio object
    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )#Create a stream to capture data from microphone
    try:
        while True:
            # Read audio from stream
            audio_data = stream.read(CHUNK_SIZE)
            #Creates a generator(iterator), function continues when data is iterated
            yield audio_data
    finally:
        # Closes when termination
        stream.stop_stream()
        stream.close()
        p.terminate()

def check_speech(iterator,vad):
    try:
        audio_data = next(iterator)
        audio_data_bytes = np.frombuffer(audio_data, dtype=np.int16).tobytes()
        return(vad.is_speech(audio_data_bytes,SAMPLE_RATE))  
    except StopIteration:
        return False  

def transcribe(model, iterator,vad):
    #Obtaining whole phrase
    acum = [] #variable to store the audio for the phrase
    while True:
        try:
            audio_data = next(iterator)
            audio_data_bytes = np.frombuffer(audio_data, dtype=np.int16).tobytes()
            if not (vad.is_speech(audio_data_bytes,SAMPLE_RATE)):#silence detected - MIGHT NEED FUTURE CHANGES TO RECOGNIZE OR WAIT TO SAY IT IS SILENCE
                break
            acum.append(audio_data_bytes)
        except StopIteration:
            break
    #Formatting
    audio = b''.join(acum)
    audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32)
    audio_np /= np.iinfo(np.int16).max
    #Transcription
    segments, info = model.transcribe(audio_np,length_penalty= 0.1,beam_size=5,language="en")
    try:
        first_segment = next(segments)
        text = first_segment.text
        return text
    except StopIteration:
        return ""

#Main execution
model_size = "medium.en"
model = fw.WhisperModel(model_size,device="cuda",compute_type="float16")
vad = vtad.Vad()
vad.set_mode(3)#Mode 3 to be more aggresive when recognizing what is voice or noise
iterator = obtain_audio()
acum_translation = ""
while True:
    try:
        if(check_speech(iterator,vad)):
            translation=transcribe(model,iterator,vad)
            acum_translation += translation
            print(translation)
    except KeyboardInterrupt:
        print(acum_translation)
        exit(0)
