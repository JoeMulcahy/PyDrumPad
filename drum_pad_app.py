from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget, QGridLayout

from app_enums.wave_form_enum import WaveForm
from drum_pads.drum_pads_module import DrumPadModule
from file_manager.audio_file_manager import FileManager
from globals_controls.globals_settings_module import GlobalControls
from midi.app_midi import AppMidi
from sample_editor.sample_view import SampleEditor
from sound_engine.AudioChannel import AudioChannel
from sound_engine.AudioVoice import AudioVoice
from sound_engine.SoundEngine import SoundEngine
from sound_engine.SynthVoice import SynthVoice
import utility.music_notes as mn
from sound_engine.Voice import Voice


class DrumPadApp(QWidget):
    def __init__(self):
        super().__init__()
        self.__selected_pad_index = 0

        self.__file_manager = FileManager()
        self.__sound_engine = SoundEngine()

        self.__pad_voices_list = []  # list of voices associated with pad
        self.__audio_channels_list = []  # list of audio channel associated with pad

        # initialise sound engine and audio channels
        self.__pad_voices_list = self.__create_test_pad_voices()
        self.__file_manager.get_files_list_from_directory(
            "C:\\Users\\josep\\Desktop\\PyDrumPad\\audio_files\\test_preset_1")
        self.__audio_channels_list = self.__create_audio_channels()

        self.__add_channels_to_engine()

        self.__pads_module = DrumPadModule()
        self.__global_controls = GlobalControls()

        # initialise sample editor
        self.__sample_editor = SampleEditor(self.__pad_voices_list[0].voice_data)
        self.highlight_selected(self.__selected_pad_index)

        self.__app_layout = QGridLayout()
        self.__app_layout.addWidget(self.__pads_module, 0, 0, 4, 4)
        self.__app_layout.addWidget(self.__global_controls, 0, 4, 1, 3)
        self.__app_layout.addWidget(self.__sample_editor, 1, 4, 3, 3)

        self.setLayout(self.__app_layout)

        self.__app_midi = AppMidi()

        self.__pads_module.pad_matrix_list[self.__selected_pad_index].select()
        self.__sound_engine.play()  # active sound engine

        #########################################################
        ##  Listeners
        #########################################################

        # populate global_controls.device.combobox with available devices
        self.__global_controls.device_combo_box.addItems(self.__app_midi.ports_list)
        self.__global_controls.load_preset_btn.clicked.connect(self.__load_samples_in_sequence)

        # global_controls.device.combobox listener
        self.__global_controls.device_combo_box.currentIndexChanged.connect(self.__change_port)

        # signal listeners
        self.__app_midi.mm_signal_note_on.connect(lambda on, note, vel: self.midi_trigger_note_on(on, note, vel))
        self.__app_midi.mm_signal_note_off.connect(lambda on, note: self.midi_trigger_note_off(on, note))
        self.__app_midi.mm_signal_cc.connect(lambda cc, value: self.midi_trigger_cc(cc, value))

        # listener for pressing pads
        for i, btn in enumerate(self.__pads_module.pad_matrix_list):
            button = btn.button
            button.clicked.connect(lambda clicked, index=i: self.highlight_selected(index))
            button.pressed.connect(lambda index=i: self.update_editor_waveform(index))
            button.pressed.connect(lambda index=i: self.trigger_pad(index))

        # listener for wave_viewer load sample button
        self.__sample_editor.load_sample_button.clicked.connect(lambda: self.__load_sample())

        # listeners for wave_viewer start, end, stretch and pitch
        self.__sample_editor.start_pos_dial.valueChanged.connect(self.__update_voice_start_position)
        self.__sample_editor.end_pos_dial.valueChanged.connect(self.__update_voice_end_position)
        self.__sample_editor.pitch_dial.valueChanged.connect(self.__update_voice_pitch)
        self.__sample_editor.stretch_dial.valueChanged.connect(self.__update_voice_stretch)

        # signal listeners
        self.__file_manager.files_loaded_signal.connect(lambda l: self.load_voice(l))

    def __update_voice_start_position(self, start):
        start = max(0.00, min(start / 100, 1.0))
        voice = self.__pad_voices_list[self.__selected_pad_index]
        voice.sample_start_scaling = start
        end = voice.sample_end_scaling
        voice.set_voice_start_end_position(start, end)

    def __update_voice_end_position(self, end):
        end = max(0.00, min(end / 100, 1.0))
        voice = self.__pad_voices_list[self.__selected_pad_index]
        voice.sample_end_scaling = end / 100
        start = voice.sample_start_scaling
        voice.set_voice_start_end_position(start, end)

    def __update_voice_pitch(self, value):
        value = max(0.01, min(value / 100, 1.0))  # ensure value can't be 0
        print(f'start: {value}')
        self.__pad_voices_list[self.__selected_pad_index].set_pitch(value)

    def __update_voice_stretch(self, value):
        value = max(0.01, min(value / 100, 1.0))  # ensure value can't be 0
        print(f'start: {value}')
        self.__pad_voices_list[self.__selected_pad_index].set_time_stretch(value)

    ###############################################
    # create default pad voices
    ###############################################
    def __create_test_pad_voices(self):
        temp_list = []
        for i in range(len(mn.NOTE_FREQUENCIES_LIST)):
            freq = mn.NOTE_FREQUENCIES_LIST[i]
            voice = SynthVoice(WaveForm.SIN, float(freq), 0.1, 0.0, 44100)
            temp_list.append(voice)

        return temp_list

    ###############################################
    # create audio channels for each voice
    ###############################################
    def __create_audio_channels(self):
        temp_list = []
        for i in range(len(self.__pad_voices_list)):
            audio_channel = AudioChannel(i, self.__pad_voices_list[i], volume=0.5, pan=0.5)
            temp_list.append(audio_channel)

        return temp_list

    ###############################################
    # add each audio channel to the sound engine
    ###############################################
    def __add_channels_to_engine(self):
        for channel in self.__audio_channels_list:
            self.__sound_engine.add_channel(channel)

    ###############################################
    # highlight pad and update currently_selected_pad_index
    ###############################################
    def highlight_selected(self, index):
        for pad in self.__pads_module.pad_matrix_list:
            pad.unselect()

        self.__pads_module.pad_matrix_list[index].select()
        self.__pads_module.currently_selected_pad_index = index
        self.__selected_pad_index = index

    ###############################################
    # play the sound sample associated with pad
    ###############################################
    def trigger_pad(self, index):
        self.__audio_channels_list[index].trigger()

    ###############################################
    # load sequential pads with voices
    ###############################################
    def __load_samples_in_sequence(self):
        self.__file_manager.get_files_using_explorer("directory")

    ###############################################
    # loads single pad with voice
    ###############################################
    def __load_sample(self):
        self.__file_manager.get_files_using_explorer("single")

    def load_voice(self, file_list: list):
        if len(file_list) == 1:
            self.load_voice_to_pad(str(file_list[0]), self.__selected_pad_index)
            self.update_editor_waveform(self.__selected_pad_index)
        else:
            for i in range(len(file_list)):
                self.load_voice_to_pad(str(file_list[i]),
                                       (self.__selected_pad_index + i) % len(self.__pads_module.pad_matrix_list))

            self.update_editor_waveform(self.__selected_pad_index)

    def load_voice_to_pad(self, file, pad_index):
        voice = AudioVoice(file)
        self.__pad_voices_list[pad_index] = voice
        audio_channel = AudioChannel(pad_index, voice, volume=1.0, pan=0.5)
        self.__audio_channels_list[pad_index] = audio_channel
        self.__sound_engine.update_audio_channels(self.__audio_channels_list)

    def update_editor_waveform(self, index):
        print(f'editor waveform: {index}')
        voice = self.__pad_voices_list[index]
        data = voice.original_voice_data
        self.__sample_editor.waveform_widget.sample_data = data
        self.__selected_pad_index = index

        # set dials
        self.__sample_editor.start_pos_dial = voice.sample_start_scaling
        self.__sample_editor.end_pos_dial = voice.sample_end_scaling

        # get pitch of voice
        self.__sample_editor.pitch_dial = voice.pitch_factor
        self.__sample_editor.stretch_dial = voice.stretch_factor

        self.repaint()

    def midi_trigger_note_on(self, on, note, velocity):
        index = (note - 36) + 32
        self.trigger_pad(index)
        self.highlight_selected(index)

    def midi_trigger_note_off(self, off, note):
        pass
        # print(f'midi off: {off} {note}')

    def midi_trigger_cc(self, cc, value):
        pass
        # print(f'midi cc: {cc} {value}')

    def __change_port(self, index):
        self.__app_midi.select_midi_port(index)
        self.__app_midi.open_inport()

    @property
    def sound_engine(self):
        return self.__sound_engine
