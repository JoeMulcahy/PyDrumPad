import soundfile as sf

from sound_engine.Voice import Voice


class AudioVoice(Voice):
    def __init__(self, filename_wav):
        self.__data, self.__samplerate = self.load_wav(filename_wav)
        super().__init__(self.__data, self.__samplerate)

    def load_wav(self, filename):
        self.__data, self.__samplerate = sf.read(filename, dtype='float32')
        if self.__data.ndim > 1:  # Convert to mono
            self.__data = self.__data.mean(axis=1)
        return self.__data, self.__samplerate


