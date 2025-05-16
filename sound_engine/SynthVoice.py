from app_enums.wave_form_enum import WaveForm
from sound_engine.Voice import Voice
from sound_engine.synth_waves import NoiseWave, SinWave, SawtoothWave, SquareWave, PulseWave, TriangleWave
import copy


class SynthVoice(Voice):
    def __init__(self, waveform, freq, dur, vol, samplerate=44100):
        self.__frequency = freq
        self.__duration = dur
        self.__volume = vol
        self.__samplerate = samplerate
        self.__waveform_type = waveform
        self.__waveform = self.__get_synth_waveform(waveform)
        self.__data = self.__waveform.waveform
        self.__samplerate = samplerate
        super().__init__(self.__data, self.__samplerate)

    def __get_synth_waveform(self, wave_type):
        if wave_type == WaveForm.SIN:
            return SinWave(frequency=self.__frequency, duration=self.__duration, volume=self.__volume,
                           samplerate=self.__samplerate)
        elif wave_type == WaveForm.SQUARE:
            return SquareWave(frequency=self.__frequency, duration=self.__duration, volume=self.__volume,
                              samplerate=self.__samplerate)
        elif wave_type == WaveForm.TRIANGLE:
            return TriangleWave(frequency=self.__frequency, duration=self.__duration, volume=self.__volume,
                                samplerate=self.__samplerate)
        elif wave_type == WaveForm.SAWTOOTH:
            return SawtoothWave(frequency=self.__frequency, duration=self.__duration, volume=self.__volume,
                                samplerate=self.__samplerate)
        elif wave_type == WaveForm.PULSE:
            return PulseWave(frequency=self.__frequency, duty_cycle=0.5, duration=self.__duration, volume=self.__volume,
                             samplerate=self.__samplerate)
        else:
            return NoiseWave(duration=self.__duration, volume=self.__volume, samplerate=self.__samplerate)

    def update_waveform(self, freq, dur, vol):
        self.__frequency = freq
        self.__duration = dur
        self.__volume = vol
        self.__waveform = self.__get_synth_waveform(self.__waveform_type)
        self.__data = self.__waveform.waveform
        super().update_data(self.__data)

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
        self.__waveform.frequency = self.__frequency
        self.__data = self.__waveform.waveform  # Get the new waveform data
        super().update_data(self.__data)  # Update the data in the Voice class

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
