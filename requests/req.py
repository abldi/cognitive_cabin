import os
import wave
import faster_whisper as fw
import pyaudio

def transcribe_chunk(model, chunk_file):
    segments, info = model.transcribe(chunk_file,length_penalty= 0.1,beam_size=5,vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500, min_speech_duration_ms=100),language="en")
    try:
        first_segment = next(segments)
        text = first_segment.text
        return text
    except StopIteration:
        return ""

#Chunk length represents the seconds each chunk is recorded - In the future might change to recording more chunks and concatenating them
def record_chunk(p, stream, file_path, chunk_length=2):
    frames=[]
    for _ in range(0, int(16000/1024*chunk_length)):
        data = stream.read(1024)
        frames.append(data)
    
    wf = wave.open(file_path,"wb")
    wf.setnchannels(1)
    wf.setframerate(16000)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.writeframes(b''.join(frames))
    wf.close()

def main2():
    #Model settings
    model_size = "medium.en"
    model = fw.WhisperModel(model_size,device="cuda",compute_type="float16")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=1024)

    acum_transcription = ""

    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p,stream,chunk_file)
            transcription = transcribe_chunk(model,chunk_file)
            print(transcription)
            os.remove(chunk_file)

            acum_transcription +=transcription + " "
    except KeyboardInterrupt:
        print("Stopping...")
        with open("log.txt","w") as log_file:
            log_file.write(acum_transcription)
    finally:
        print("LOG" + acum_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main2()