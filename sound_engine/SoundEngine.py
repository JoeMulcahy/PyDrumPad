import threading

import numpy as np
import sounddevice as sd

from sound_engine import AudioChannel


class SoundEngine:
    def __init__(self, samplerate=44100):
        self.__channels = []
        self.__samplerate = samplerate
        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=2,
            dtype='float32',
            callback=self.audio_callback
        )
        self.lock = threading.Lock()
        self.current_time = 0  # Keep track of the current time.
        self.block_duration = 0.0  # Store the duration of each audio callback block
        self.__master_volume = 0.5

    def audio_callback(self, outdata, frames, time, status):
        with self.lock:
            mix = np.zeros((frames, 2), dtype=np.float32)
            self.block_duration = frames / self.__samplerate  # Calculate duration of the block
            self.current_time += self.block_duration

            for channel in self.__channels:
                if channel.is_playing:
                    chunk = channel.next_stereo_chunk(frames) * self.__master_volume
                    mix += chunk

                    # Check if the voice is finished playing.
                    if not channel.voice.active:  # Changed to check channel.voice.__active
                        channel.is_playing = False

            # Clip to avoid overflow
            np.clip(mix, -1.0, 1.0, out=outdata)

    def update_audio_channels(self, audio_channels):
        with self.lock:
            self.__channels = audio_channels

    def add_channel(self, channel: AudioChannel):
        with self.lock:
            self.__channels.append(channel)

    def remove_channel(self, channel):
        with self.lock:
            self.__channels.remove(channel)

    def play(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()

    def get_current_time(self):
        return self.current_time

    def set_master_volume(self, value):
        self.__master_volume = value

    @property
    def sample_rate(self):
        return self.__samplerate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__samplerate = value

    @property
    def channels(self):
        return self.__channels
