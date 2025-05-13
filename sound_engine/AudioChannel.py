import numpy as np
from scipy.signal import sosfiltfilt, butter
import math
from scipy.signal import sosfiltfilt, sosfilt

from sound_engine import Voice


class AudioChannel:
    def __init__(self, channel_id, voice: Voice, volume=1.0, pan=0.0):
        self.__id = channel_id
        self.__voice = voice
        self.__volume = volume  # 0.0 to 1.0
        self.__pan = pan  # -1.0 (L) to 1.0 (R)
        self.is_playing = False  # Add is_playing attribute
        self.start_time = 0  # Add start_time attribute

        self.__hsf_gain = 0.0  # High shelf gain in dB
        self.__hsf_cutoff = 2000.0  # High shelf cutoff frequency

        self.__lsf_gain = 0.0  # Low shelf gain in dB
        self.__lsf_cutoff = 100.0  # Low shelf cutoff frequency

        self.__is_muted = False

    def next_stereo_chunk(self, frames: int) -> np.ndarray:
        if not self.is_playing or self.__is_muted:
            return np.zeros((frames, 2), dtype=np.float32)

        mono = self.__voice.next_chunk(frames) * self.__volume

        if mono.ndim > 1:
            mono = mono.squeeze(axis=1)
            mono = self.apply_shelving_eq(mono)

        # Simple equal-power panning
        left = mono * np.cos((self.__pan + 1) * np.pi / 4)
        right = mono * np.sin((self.__pan + 1) * np.pi / 4)
        return np.stack([left, right], axis=-1)

    def trigger(self, start_time=0):
        """Start playing the voice from the beginning."""
        self.__voice.reset_position()
        self.is_playing = True
        self.start_time = start_time  # Store start time

    def stop(self):
        """Stop playing the voice."""
        self.is_playing = False

    def set_hsf_gain(self, value):
        # value is between 0 and 100
        """Set the high shelf gain in dB."""
        self.__hsf_gain = (value - 50) * 0.3  # scale 15db to +15db

    def set_hsf_cutoff(self, cutoff_frequency):
        """Set the high shelf cutoff frequency."""
        self.__hsf_cutoff = cutoff_frequency

    def set_lsf_gain(self, value):
        # value is between 0 and 100
        """Set the low shelf gain in dB."""
        self.__lsf_gain = (value - 50) * 0.3  # scale 15db to +15db

    def set_lsf_cutoff(self, cutoff_frequency):
        """Set the low shelf cutoff frequency."""
        self.__lsf_cutoff = cutoff_frequency

    def apply_shelving_eq(self, data=None):
        """Apply proper high and low shelving filters."""
        if data is None:
            return None

        if self.__lsf_gain != 0:
            data = self.shelving_filter(data, self.__lsf_gain, self.__lsf_cutoff, self.voice.sample_rate,
                                        shelf_type='low')

        if self.__hsf_gain != 0:
            data = self.shelving_filter(data, self.__hsf_gain, self.__hsf_cutoff, self.voice.sample_rate,
                                        shelf_type='high')

        return data

    def shelving_filter(self, data, gain_db, cutoff, sample_rate, shelf_type='low'):
        """
        Apply a low or high shelving filter.
        """
        amplitude = 10 ** (gain_db / 40)
        w0 = 2 * np.pi * cutoff / sample_rate
        alpha = np.sin(w0) / 2 * np.sqrt((amplitude + 1 / amplitude) * (1 / 0.707 - 1) + 2)

        cos_w0 = np.cos(w0)

        if shelf_type == 'low':
            b0 = amplitude * ((amplitude + 1) - (amplitude - 1) * cos_w0 + 2 * np.sqrt(amplitude) * alpha)
            b1 = 2 * amplitude * ((amplitude - 1) - (amplitude + 1) * cos_w0)
            b2 = amplitude * ((amplitude + 1) - (amplitude - 1) * cos_w0 - 2 * np.sqrt(amplitude) * alpha)
            a0 = (amplitude + 1) + (amplitude - 1) * cos_w0 + 2 * np.sqrt(amplitude) * alpha
            a1 = -2 * ((amplitude - 1) + (amplitude + 1) * cos_w0)
            a2 = (amplitude + 1) + (amplitude - 1) * cos_w0 - 2 * np.sqrt(amplitude) * alpha
        elif shelf_type == 'high':
            b0 = amplitude * ((amplitude + 1) + (amplitude - 1) * cos_w0 + 2 * np.sqrt(amplitude) * alpha)
            b1 = -2 * amplitude * ((amplitude - 1) + (amplitude + 1) * cos_w0)
            b2 = amplitude * ((amplitude + 1) + (amplitude - 1) * cos_w0 - 2 * np.sqrt(amplitude) * alpha)
            a0 = (amplitude + 1) - (amplitude - 1) * cos_w0 + 2 * np.sqrt(amplitude) * alpha
            a1 = 2 * ((amplitude - 1) - (amplitude + 1) * cos_w0)
            a2 = (amplitude + 1) - (amplitude - 1) * cos_w0 - 2 * np.sqrt(amplitude) * alpha
        else:
            raise ValueError("shelf_type must be 'low' or 'high'")

        # Normalize coefficients
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1.0, a1 / a0, a2 / a0])

        return sosfiltfilt([[b[0], b[1], b[2], a[0], a[1], a[2]]], data)

    @property
    def channel_id(self):
        return self.__id

    @property
    def voice(self):
        return self.__voice

    @property
    def volume(self):
        return self.__volume

    @property
    def pan(self):
        return self.__pan

    @voice.setter
    def voice(self, value):
        self.__voice = value

    @volume.setter
    def volume(self, value):
        self.__volume = value

    @pan.setter
    def pan(self, value):
        self.__pan = value

    @property
    def is_muted(self):
        return self.__is_muted

    @is_muted.setter
    def is_muted(self, value):
        self.__is_muted = value
