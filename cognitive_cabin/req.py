import os
import sys
import wave
import faster_whisper as fw
import pyaudio


def transcribe_chunk(model, chunk_file, use_VAD=True):
    segments, info = model.transcribe(chunk_file, length_penalty=0.1, beam_size=5, vad_filter=use_VAD,
                                      vad_parameters=dict(min_silence_duration_ms=500, min_speech_duration_ms=100),
                                      language="en")
    try:
        text = ""
        for seg in segments:
            text = text + seg.text
        return text
    except StopIteration:
        return ""


# Chunk length represents the seconds each chunk is recorded - In the future might change to recording more chunks and
# concatenating them
def record_chunk(p, stream, file_path, chunk_length=2):
    frames = []
    for _ in range(0, int(16000 / 1024 * chunk_length)):
        data = stream.read(1024)
        frames.append(data)

    wf = wave.open(file_path, "wb")
    wf.setnchannels(1)
    wf.setframerate(16000)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.writeframes(b''.join(frames))
    wf.close()


if __name__ == "__main__":
    # Model settings
    model_size = "small.en"
    model = fw.WhisperModel(model_size, device="cuda", compute_type="float16")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    acc_transcription = ""
    chunk_file = "temp_chunk.wav"

    try:
        if len(sys.argv) > 1:
            transcription = transcribe_chunk(model, sys.argv[1], use_VAD=False)
            acc_transcription += transcription + " "
        else:
            while True:
                record_chunk(p, stream, chunk_file)
                transcription = transcribe_chunk(model, chunk_file)
                print(f"RTT: {transcription}")
                os.remove(chunk_file)

                acc_transcription += transcription + " "
    except KeyboardInterrupt:
        print("Stopping...")
        with open("log.txt", "w") as log_file:
            log_file.write(acc_transcription)
    finally:
        print("LOG" + acc_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()