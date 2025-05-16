import copy
import threading
import sounddevice as sd
import librosa
import numpy as np


class Voice:
    def __init__(self, data: np.ndarray, samplerate: int):
        self.__data = data
        self.__data_manipulated = self.__data.copy()
        self.__original_data = self.__data.copy()
        self.__samplerate = samplerate
        self.__original_sample_rate = samplerate
        self.__original_voice_length = self.__original_data.shape[0]
        self.__position = 0  # Current playback index
        self.__end_position = 0 # end of sample
        self.__sample_start = 0 # where to begin sample playback
        self.__sample_end = 0   # where to end sample playback
        self.__sample_start_scaling = 0.0   # used to determine self.__sample_start, 0.0 t0 1.0
        self.__sample_end_scaling = 0.0  # used to determine self.__sample_end, 0.0 t0 1.0
        self.__active = True
        self._playback_thread = None  # To keep track of the playback thread
        self.__pitch_factor = 0.5  # Default pitch factor (1.0 means no change)
        self.__stretch_factor = 0.5

    def update_data(self, updated_data):
        self.__data = copy.deepcopy(updated_data)

    def next_chunk(self, frames: int) -> np.ndarray:
        """Return the next chunk of audio data."""
        if not self.__active:
            return np.zeros((frames, self.__data.shape[1] if self.__data.ndim > 1 else 1),
                            dtype=np.float32)

        if self.__position >= len(self.__data):
            self.__active = False
            return np.zeros((frames, self.__data.shape[1] if self.__data.ndim > 1 else 1),
                            dtype=np.float32)

        self.__end_position = self.__position + frames
        print(f'in chunk start {self.__position} end: {self.__end_position}')
        chunk = self.__data[self.__position:self.__end_position]

        # Ensure chunk is 2D
        if chunk.ndim == 1:
            chunk = chunk[:, np.newaxis]  # Add a channel dimension
        elif chunk.ndim > 2:
            chunk = chunk.squeeze(axis=1)

        self.__position = self.__end_position

        # Pad with zeros if end of audio
        if len(chunk) < frames:
            padding = np.zeros(
                (frames - len(chunk), self.__data.shape[1] if self.__data.ndim > 1 else 1),
                dtype=np.float32)
            chunk = np.concatenate((chunk, padding), axis=0)

        return chunk

    def set_voice_start_end_position(self, start, end):
        self.__sample_start_scaling = start
        self.__sample_end_scaling = end

        temp_data = self.__original_data
        data_length = temp_data.shape[0]

        self.__sample_end = int(data_length * (1.0 - end))  # calculate end sample
        self.__sample_start = int(data_length * start)  # calculate starting sample

        print('-----------------------------------------------------')
        print(f'sample len: {data_length}')
        print(f'scale_start: {self.__sample_start_scaling}  scale_end: {self.__sample_end_scaling}')
        print(f'sample_start: {self.__sample_start}  sample_end: {self.__sample_end}')

        # Handle mono or stereo safely
        if temp_data.ndim == 1:  # Mono
            temp_data = temp_data[self.__sample_start:self.__sample_end]
        elif temp_data.ndim == 2:  # Stereo (or more channels)
            temp_data = temp_data[self.__sample_start:self.__sample_end, :]
        else:
            raise ValueError("Unsupported audio data shape: expected 1D or 2D array.")

        self.__data = temp_data
        self.reset_position()  # Important to reset playback!

    ############################################################################
    ## Alter pitch of voice using resampling
    ############################################################################
    def set_pitch(self, pitch_factor):
        """Alter the pitch by adjusting the pitch factor."""
        self.__pitch_factor = pitch_factor * 2
        self.__resample_audio()

    def __resample_audio(self):
        new_samplerate = self.__original_sample_rate * (1 / self.__pitch_factor)
        if new_samplerate <= self.__original_sample_rate / 4:
            new_samplerate = self.__original_sample_rate / 4

        if new_samplerate >= self.__original_sample_rate * 4:
            new_samplerate = self.__original_sample_rate * 4

        print(f"Resampling audio from {self.__samplerate}Hz to {new_samplerate}Hz.")
        # Check if self.__data is a numpy array
        if not isinstance(self.__data, np.ndarray):
            raise TypeError(f"Expected self.__data to be a numpy array, but got {type(self.__data)}")

        # Check if self.__data is 1D or 2D
        if self.__data.ndim > 2:
            raise ValueError(f"Expected self.__data to be 1D or 2D, but got {self.__data.ndim}D")

        # Ensure the data type is float32 or float64
        if self.__data.dtype not in [np.float32, np.float64]:
            raise TypeError(f"Expected self.__data to be of dtype float32 or float64, but got {self.__data.dtype}")

        try:
            # Perform the resampling using librosa
            self.__data_manipulated = librosa.resample(self.__data, orig_sr=self.__samplerate, target_sr=new_samplerate)
            self.__samplerate = new_samplerate  # Update the samplerate
            self.__data = self.__data_manipulated
        except Exception as e:
            print(f"Error during resampling: {e}")
            raise

    ############################################################################
    ##  Set voice start and end positions
    ############################################################################
    def set_voice_start_and_end_position(self, start, end):
        if start < end:
            print(f'start:{start} end:{end}')
            total_samples = self.__data.shape[0]
            self.__position = int(start * total_samples)
            self.__end_position = int(total_samples - (total_samples * end))
        else:
            print('start cant be greater than end')

    ############################################################################
    ## Alter voice duration
    ############################################################################
    def set_voice_length(self, scaled_duration):
        scaled_duration = np.clip(scaled_duration, 0.0, 1.0)  # ensure duration scale is between 0.0 and 1.0 (from UI)
        temp_data = self.__data.copy()

        # Calculate the desired number of samples from voice for playback
        target_duration_samples = int(temp_data.shape[0] * scaled_duration)

        # Handle mono or stereo safely
        if temp_data.ndim == 1:  # Mono
            self.__data_manipulated = temp_data[:target_duration_samples]
        elif temp_data.ndim == 2:  # Stereo (or more channels)
            self.__data_manipulated = temp_data[:target_duration_samples, :]
        else:
            raise ValueError("Unsupported audio data shape: expected 1D or 2D array.")

        self.__data = self.__data_manipulated
        self.reset_position()  # Important to reset playback!

    def set_time_stretch(self, stretch_scale):
        self.__stretch_factor = stretch_scale
        stretch_scale = stretch_scale * 3  # (optional: clip first)

        if stretch_scale <= 0:
            self.__data = np.zeros_like(self.__original_data)
            return

        temp_data = self.__original_data.copy()
        current_duration_samples = temp_data.shape[0]

        desired_duration_seconds = stretch_scale * (current_duration_samples / self.__samplerate)
        desired_num_samples = int(desired_duration_seconds * self.__samplerate)

        if desired_num_samples <= 0:
            self.__data = np.zeros_like(self.__original_data.copy())
            return

        stretch_ratio = current_duration_samples / desired_num_samples

        if temp_data.ndim == 1:
            # MONO audio
            stretched = librosa.effects.time_stretch(temp_data, rate=stretch_ratio)
            self.__data_manipulated = stretched
        elif temp_data.ndim == 2:
            # STEREO audio
            # Stretch each channel separately
            left = librosa.effects.time_stretch(temp_data[:, 0], rate=stretch_ratio)
            right = librosa.effects.time_stretch(temp_data[:, 1], rate=stretch_ratio)
            self.__data_manipulated = np.stack((left, right), axis=-1)
        else:
            raise ValueError("Unsupported audio shape. Expected 1D (mono) or 2D (stereo) array.")

        self.__data = self.__data_manipulated
        self.reset_position()

    def preview_voice(self, is_pre=True):
        if self._playback_thread and self._playback_thread.is_alive():
            print(f"Warning: sound is already playing.")
            return  # Important: Return, don't start a new thread

        self._playback_thread = threading.Thread(target=self.__play_audio(is_pre))
        self._playback_thread.start()
        print(f"Started playback of: sound on a new thread.")

    def __play_audio(self, is_pre):
        try:
            if is_pre:
                sd.play(self.__original_data, self.__samplerate)
            else:
                sd.play(self.__data_manipulated, self.__samplerate)

            # sd.wait()
        except Exception as e:
            print(f"Error during playback of sound: {e}")
        finally:
            self._playback_thread = None  # Reset the thread

    def reset_position(self):
        """Reset the playback position to the beginning of the sound."""
        self.__position = self.sample_start
        self.__active = True  # Make sure the voice is active when it is reset

    @property
    def active(self):
        return self.__active

    @active.setter
    def active(self, value):
        self.__active = value

    @property
    def sample_rate(self):
        return self.__samplerate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__samplerate = value

    def reset_voice(self):
        self.__data = self.__original_data
        self.__samplerate = self.__original_sample_rate

    @property
    def original_voice_data(self):
        return self.__original_data

    @property
    def voice_data(self):
        return self.__data

    @property
    def position(self):
        return self.__position

    @property
    def end_position(self):
        return self.__end_position

    @property
    def sample_start(self):
        return self.__sample_start

    @sample_start.setter
    def sample_start(self, value):
        self.__sample_start = value

    @property
    def sample_end(self):
        return self.__sample_end

    @sample_end.setter
    def sample_end(self, value):
        self.__sample_end = value

    @property
    def sample_start_scaling(self):
        return self.__sample_start_scaling

    @sample_start_scaling.setter
    def sample_start_scaling(self, value):
        self.__sample_start_scaling = value

    @property
    def sample_end_scaling(self):
        return self.__sample_end_scaling

    @sample_end_scaling.setter
    def sample_end_scaling(self, value):
        self.__sample_end_scaling = value

    @property
    def pitch_factor(self):
        return self.__pitch_factor

    @pitch_factor.setter
    def pitch_factor(self, value):
        self.__pitch_factor = value
        self.set_pitch(value)

    @property
    def stretch_factor(self):
        return self.__stretch_factor

    @stretch_factor.setter
    def stretch_factor(self, value):
        self.__stretch_factor = value
        self.set_time_stretch(value)
