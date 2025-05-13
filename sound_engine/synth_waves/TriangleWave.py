import numpy as np

from sound_engine.synth_waves.SynthWaveform import SynthWaveform


class TriangleWave(SynthWaveform):
    def __init__(self, frequency, volume, duration, samplerate=44100):
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        wave = volume * (2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1)
        super().__init__(wave, frequency, volume, duration, samplerate)
