import numpy as np

from sound_engine.Voice import Voice


class SynthWaveform:
    def __init__(self, waveform, frequency, volume, duration, samplerate):
        self.__waveform = waveform
        self.__frequency = frequency
        self.__volume = volume
        self.__duration = duration
        self.__samplerate = samplerate

    @property
    def waveform(self):
        return self.__waveform

    @waveform.setter
    def waveform(self, value):
        self.__waveform = value

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        self.__frequency = value

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        self.__volume = value

    @property
    def duration(self):
        return self.__duration

    @duration.setter
    def duration(self, value):
        self.__duration = value

    @property
    def samplerate(self):
        return self.__samplerate

    @samplerate.setter
    def samplerate(self, value):
        self.__samplerate = value
