import numpy as np

from sound_engine.synth_waves.SynthWaveform import SynthWaveform


class NoiseWave(SynthWaveform):
    def __init__(self, volume, duration, samplerate=44100):
        num_samples = int(samplerate * duration)
        wave = volume * (2 * np.random.rand(num_samples) - 1)
        super().__init__(wave, frequency=440, volume=0.5, duration=1.0, samplerate=44100)
