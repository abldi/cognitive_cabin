import io
import os.path
import tempfile
import threading
import time
import faster_whisper as fw
import webrtcvad
import pyaudio
from pydub import AudioSegment
from pydub.utils import make_chunks


def list_audio_devices():
    p = pyaudio.PyAudio()

    print("Available audio devices:")
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        print(f"{i}: {device_info.get('name')}")


class AudioAnalysis:
    thread_lock = None
    audio_to_process = None
    vad = None
    model = None
    p = None
    stream = None
    max_audio_buffer_length = 15
    _observers = []

    rate = 16000

    def __init__(self, conf_file, model_name='small.en'):
        self.thread_lock = threading.Lock()
        self.audio_to_process = AudioSegment.empty()
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
        self.model = fw.WhisperModel(model_name, device="cuda", compute_type="float16")
        self.p = pyaudio.PyAudio()
        self.device_index = 0

        if os.path.exists(conf_file):
            with open(conf_file, 'r') as file:
                file_content = file.read()
                self.device_index = int(file_content.strip())
        else:
            with open(conf_file, 'w') as file:
                file.write(str(self.device_index))

        self.stream = self.p.open(input_device_index=self.device_index,
                                  format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=1024,
                                  stream_callback=self.stream_record_callback)

    def test_compatibility(self):
        p = pyaudio.PyAudio()
        sample_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 96000]
        audio_format = pyaudio.paInt16
        channels = 1

        print(f"Supported sample rates for device {self.device_index}:")
        for rate in sample_rates:
            try:
                if p.is_format_supported(rate,
                                         input_device=self.device_index,
                                         input_channels=channels,
                                         input_format=audio_format):
                    print(f"{rate} Hz")
            except ValueError:
                # This sample rate is not supported
                pass

        p.terminate()

    def add_observer(self, observer):
        self._observers.append(observer)

    def stream_record_callback(self, in_data, frame_count, time_info, status):
        new_audio = AudioSegment.from_raw(io.BytesIO(in_data), sample_width=2, frame_rate=self.rate, channels=1)

        self.thread_lock.acquire()
        self.audio_to_process += new_audio
        self.thread_lock.release()

        return None, pyaudio.paContinue

    def transcribe_chunk(self, chunk_file):
        segments, info = self.model.transcribe(chunk_file, length_penalty=0.1, beam_size=5, vad_filter=False,
                                               language="en")
        try:
            first_segment = next(segments)
            text = first_segment.text
            return text
        except StopIteration:
            return ""

    def run_forever_in_thread(self):
        thread = threading.Thread(target=self.run_forever)
        thread.start()

        return thread

    def run_forever(self):
        try:
            while True:
                if self.audio_to_process.duration_seconds < 1:
                    time.sleep(1 - self.audio_to_process.duration_seconds)
                    continue

                chunk_duration_ms = 30
                chunks = list(reversed(make_chunks(self.audio_to_process, chunk_duration_ms)))

                for i, chunk in enumerate(chunks[1:]):
                    if (not self.vad.is_speech(chunk.raw_data, self.rate) or
                            self.audio_to_process.duration_seconds > self.max_audio_buffer_length):
                        split_at = (len(chunks) - i - 1) * chunk_duration_ms
                        part_to_process = self.audio_to_process[0:split_at]
                        self.audio_to_process = self.audio_to_process[split_at:]

                        if self.audio_to_process.duration_seconds > self.max_audio_buffer_length:
                            print(f"audio length is {self.audio_to_process.duration_seconds} | we split at {split_at}, on total of {len(chunks)}")

                        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.wav')
                        part_to_process.export(temp_file.name, format="wav")
                        transcription = self.transcribe_chunk(temp_file.name).strip()

                        for observer in self._observers:
                            observer(transcription)

                        # if transcription != '':
                        #     now = datetime.datetime.now()
                        #     transcripts.append({
                        #         'start': now,
                        #         'transcript': transcription,
                        #         'end': now + datetime.timedelta(seconds=split_at / 1000)})
                        break

        finally:
            print("Closing stream")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
