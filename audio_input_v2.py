import faster_whisper as fw
import noisereduce as nr
import pyaudio
import webrtcvad as vtad
import numpy as np

# Global Constants
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
CHANNELS = 1
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
FILE_NAME = "tmp_reducednoise.wav"


# Functions
def obtain_audio():
    p = pyaudio.PyAudio()  # Initialize pyaudio object

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Device {i}: {info['name']}, Channels: {info['maxInputChannels']}")

    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
        input_device_index=10
    )
    stream.start_stream()
    active = stream.is_active()

    try:
        while True:
            # Read audio from stream
            audio_data = stream.read(CHUNK_SIZE)
            # Creates a generator(iterator), function continues when data is iterated
            yield audio_data
    except Exception as e:
        print(e)
    finally:
        # Closes when termination
        stream.stop_stream()
        stream.close()
        p.terminate()


def check_speech(iterator, vad):
    try:
        audio_data = next(iterator)
        audio_data_bytes = np.frombuffer(audio_data, dtype=np.int16)
        # Try to reduce the noise though is a small chunk
        noisered_data = nr.reduce_noise(y=audio_data_bytes, sr=16000, prop_decrease=1)
        return (vad.is_speech(noisered_data, SAMPLE_RATE))
    except StopIteration:
        return False


def transcribe(model, iterator, vad):
    # Obtaining whole phrase
    acum = []  # variable to store the audio for the phrase
    while True:
        try:
            audio_data = next(iterator)
            audio_data_bytes = np.frombuffer(audio_data, dtype=np.int16).tobytes()
            if not (vad.is_speech(audio_data_bytes,
                                  SAMPLE_RATE)):  # silence detected - MIGHT NEED FUTURE CHANGES TO RECOGNIZE OR WAIT TO SAY IT IS SILENCE
                break
            acum.append(audio_data_bytes)
        except StopIteration:
            break
    # Formatting
    audio = b''.join(acum)
    audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32)
    audio_np /= np.iinfo(np.int16).max
    # Transcription
    segments, info = model.transcribe(audio_np, length_penalty=0.1, beam_size=5, language="en")
    try:
        first_segment = next(segments)
        text = first_segment.text
        # os.remove(FILE_NAME)#noise reduction removed
        return text
    except StopIteration:
        return ""


# Main execution
model_size = "medium.en"
model = fw.WhisperModel(model_size, device="cuda", compute_type="float16")
vad = vtad.Vad()
vad.set_mode(3)  # Mode 3 to be more aggresive when recognizing what is voice or noise
iterator = obtain_audio()
acum_translation = ""
while True:
    try:
        if (check_speech(iterator, vad)):
            translation = transcribe(model, iterator, vad)
            acum_translation += translation
            print(translation)
    except KeyboardInterrupt:
        print(acum_translation)
        exit(0)
