import sys
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

        self.device_list = []

    def audio_callback(self, outdata, frames, time, status):
        with self.lock:
            mix = np.zeros((frames, 2), dtype=np.float32)
            self.block_duration = frames / int(self.__samplerate)   # Calculate duration of the block
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

    def list_audio_devices(self):
        """Prints a list of audio devices."""
        devices = sd.query_devices()
        default_input_device_index = sd.default.device[0]
        default_output_device_index = sd.default.device[1]
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']} (Driver: {device['hostapi']})")
            if i == default_input_device_index:
                print(f"  (Default Input Device)")
            if i == default_output_device_index:
                print(f"  (Default Output Device)")
            # The following code will cause an error on systems without MIDI support
            if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
                try:
                    default_midi_input_device_index = sd.default.midi_input
                    default_midi_output_device_index = sd.default.midi_output
                    if i == default_midi_input_device_index:
                        print(f"  (Default MIDI Input Device)")
                    if i == default_midi_output_device_index:
                        print(f"  (Default MIDI Output Device)")
                except AttributeError:
                    print("  (No default MIDI devices)")

    if __name__ == "__main__":
        list_audio_devices()

    def get_default_devices(self):
        devices = sd.query_devices()
        default_input_device_index = sd.default.device[0]
        default_output_device_index = sd.default.device[1]
        default_midi_input_device_index = sd.default.midi_input
        default_midi_output_device_index = sd.default.midi_output

        for i, device in enumerate(devices):
            # print(f"Device {i}: {device['name']}")
            if i == default_input_device_index:
                print(f"  (Default Input Device)")
                print(f"Device {i}: {device['name']}")
            if i == default_output_device_index:
                print(f"  (Default Output Device)")
                print(f"Device {i}: {device['name']}")
            if i == default_midi_input_device_index:
                print(f"  (Default MIDI Input Device)")
                print(f"Device {i}: {device['name']}")
            if i == default_midi_output_device_index:
                print(f"  (Default MIDI Output Device)")
                print(f"Device {i}: {device['name']}")




    @property
    def sample_rate(self):
        return self.__samplerate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__samplerate = value

    @property
    def channels(self):
        return self.__channels
