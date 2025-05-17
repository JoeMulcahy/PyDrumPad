import os
import shelve

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QMessageBox, QInputDialog, QFileDialog

import settings
from app_enums.wave_form_enum import WaveForm
from drum_pads.drum_pads_module import DrumPadModule
from file_manager.audio_file_manager import FileManager
from globals_controls.globals_settings_module import GlobalControls
from midi.app_midi import AppMidi
from sample_editor.sample_editor import SampleEditor
from sound_engine.AudioChannel import AudioChannel
from sound_engine.AudioVoice import AudioVoice
from sound_engine.SoundEngine import SoundEngine
from sound_engine.SynthVoice import SynthVoice
import utility.music_notes as mn
from sound_engine.Voice import Voice


class DrumPadApp(QWidget):
    restart_requested_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__selected_pad_index = 0

        self.__file_manager = FileManager()
        self.__sound_engine = SoundEngine()
        # self.__sound_engine.list_audio_devices()

        self.__pad_voices_list = []  # list of voices associated with pad
        self.__audio_channels_list = []  # list of audio channel associated with pad

        # create default voices for pads
        self.__pad_voices_list = self.__create_empty_pad_voices()

        # load test samples, comment out to start with no samples loaded
        self.__file_manager.get_files_list_from_directory(
            "C:\\Users\\josep\\Desktop\\PyDrumPad\\audio_files\\test_preset_1")
        self.__audio_channels_list = self.__create_audio_channels()

        self.__filenames_list = ["" for s in range(len(self.__pad_voices_list))]

        self.__add_channels_to_engine()

        self.__pads_module = DrumPadModule()
        self.__global_controls = GlobalControls()

        # initialise sample editor
        self.__sample_editor = SampleEditor(self.__pad_voices_list[0].voice_data)

        self.__app_layout = QGridLayout()
        self.__app_layout.addWidget(self.__pads_module, 0, 0, 4, 4)
        self.__app_layout.addWidget(self.__global_controls, 0, 4, 1, 3)
        self.__app_layout.addWidget(self.__sample_editor, 1, 4, 3, 3)

        self.setLayout(self.__app_layout)

        self.__app_midi = AppMidi()
        # self.__change_port(1)

        self.__pads_module.pad_matrix_list[self.__selected_pad_index].select()
        self.__sound_engine.play()  # active sound engine

        #########################################################
        ##  Listeners
        #########################################################

        # populate global_controls.device.combobox with available devices
        self.__global_controls.device_combo_box.addItems(self.__app_midi.ports_list)

        # preset. partially implemented, loads sequence of samples to pads
        # self.__global_controls.load_preset_btn.clicked.connect(self.__load_samples_in_sequence)
        self.__global_controls.load_preset_btn.clicked.connect(self.__load_preset)
        self.__global_controls.save_preset_btn.clicked.connect(self.__save_preset)

        # reset app
        self.__global_controls.reset_preset_btn.clicked.connect(self.__reset_application)

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

        self.__pads_module.load_button.clicked.connect(lambda: self.__load_sample())
        self.__pads_module.load_directory_button.clicked.connect(lambda: self.__load_samples_in_sequence())

        # listener for wave_viewer load sample button
        self.__sample_editor.load_sample_button.clicked.connect(lambda: self.__load_sample())

        # listeners for sample editor start, end, stretch and pitch
        self.__sample_editor.start_pos_dial.valueChanged.connect(self.__update_voice_start_position)
        self.__sample_editor.end_pos_dial.valueChanged.connect(self.__update_voice_end_position)
        self.__sample_editor.pitch_dial.valueChanged.connect(self.__update_voice_pitch)
        self.__sample_editor.stretch_dial.valueChanged.connect(self.__update_voice_stretch)
        self.__sample_editor.volume_dial.valueChanged.connect(self.__update_channel_volume)
        self.__sample_editor.pan_dial.valueChanged.connect(self.__update_channel_pan)

        # signal listeners
        self.__file_manager.files_loaded_signal.connect(lambda l: self.load_voice(l))

        self.highlight_selected(self.__selected_pad_index)

    def __load_preset(self):
        options = QFileDialog.Option(0)

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select a preset",
            f"{settings.Settings.PRESETS_DIR}",
            "Preset Files (*.dat);;",
            options=options
        )

        if filename:
            setting_dict = {}
            base_filename = os.path.splitext(filename)[0]
            try:
                with shelve.open(base_filename) as db:
                    for key, value in db.items():
                        setting_dict[key] = value
            except Exception as e:
                print(f'Error: {e}')

            print(setting_dict)
        else:
            return

        preset_name = setting_dict['preset_name']
        for i in range(len(self.__pad_voices_list)):
            pad_setting = setting_dict[f'{i}']
            filename = pad_setting['file_name']
            pad_voice_data = pad_setting['pad_voice_data']
            volume = pad_setting['volume']
            pan = pad_setting['pan']
            start = pad_setting['start']
            end = pad_setting['end']
            pitch = pad_setting['pitch']
            stretch = pad_setting['stretch']

            self.__filenames_list[i] = filename

            self.__pad_voices_list[i].voice_data = pad_voice_data
            # self.__pad_voices_list[i].sample_start_scaling = start
            # self.__pad_voices_list[i].sample_end_scaling = end
            # self.__pad_voices_list[i].pitch_factor = pitch
            # self.__pad_voices_list[i].stretch_factor = stretch

            # self.__audio_channels_list[i].volume = volume
            # self.__audio_channels_list[i].pan = pan

        # for channel in self.__audio_channels_list:
        #     self.sound_engine.update_audio_channels(channel)
        #
        # self.highlight_selected(0)
        # self.update_editor_waveform(0)

    def __save_preset(self):
        user_input, ok = QInputDialog.getText(
            self,
            "Save preset",
            "Enter preset name"
        )

        if ok:
            preset_dict = {}
            preset_name = user_input

            preset_dict['preset_name'] = preset_name

            for i in range(len(self.__pad_voices_list)):
                settings_dict = {}
                pad_number = i
                settings_dict["file_name"] = self.__filenames_list[i]
                settings_dict["pad_voice_data"] = self.__pad_voices_list[i].original_voice_data
                settings_dict["volume"] = self.__audio_channels_list[i].volume
                settings_dict["pan"] = self.__audio_channels_list[i].pan_scaled
                settings_dict["start"] = self.__sample_editor.start_pos_dial = self.__pad_voices_list[
                    i].sample_start_scaling
                settings_dict["end"] = self.__sample_editor.end_pos_dial = self.__pad_voices_list[i].sample_end_scaling
                settings_dict["pitch"] = self.__sample_editor.pitch_dial = self.__pad_voices_list[i].pitch_factor
                settings_dict["stretch"] = self.__sample_editor.stretch_dial = self.__pad_voices_list[i].stretch_factor

                preset_dict[str(pad_number)] = settings_dict

            file_path = os.path.join(settings.Settings.PRESETS_DIR, preset_name)
            try:
                os.makedirs(settings.Settings.PRESETS_DIR, exist_ok=True)
                with shelve.open(file_path) as db:
                    for key, value in preset_dict.items():
                        db[key] = value

                print(f'{preset_name} save to {file_path}')
            except FileNotFoundError:
                print("preset cannot be saved")
        else:
            print("User canceled restart.")
            return

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
        print(f'pitch: {value}')
        self.__pad_voices_list[self.__selected_pad_index].pitch_factor = value

    def __update_voice_stretch(self, value):
        value = max(0.01, min(value / 100, 1.0))  # ensure value can't be 0
        print(f'stretch: {value}')
        self.__pad_voices_list[self.__selected_pad_index].set_time_stretch(value)

    def __update_channel_volume(self, value):
        value = max(0.01, min(value / 100, 1.0))  # ensure value can't be 0
        print(f'vol: {value}')
        self.__audio_channels_list[self.__selected_pad_index].volume = value

    def __update_channel_pan(self, value):
        value = max(0.01, min(value / 100, 1.0))  # ensure value can't be 0
        self.__audio_channels_list[self.__selected_pad_index].pan_scaled = value

    ###############################################
    # create default pad voices
    ###############################################
    def __create_empty_pad_voices(self):
        temp_list = []
        for i in range(len(mn.NOTE_FREQUENCIES_LIST)):
            freq = mn.NOTE_FREQUENCIES_LIST[i]
            voice = SynthVoice(WaveForm.SIN, float(freq), 0.0001, 0.0, 44100)
            temp_list.append(voice)

        return temp_list

    ###############################################
    # create audio channels for each voice
    ###############################################
    def __create_audio_channels(self):
        temp_list = []
        for i in range(len(self.__pad_voices_list)):
            audio_channel = AudioChannel(i, self.__pad_voices_list[i], volume=0.5, pan_scaled=0.5)
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

    ################################################
    ##  load voices into pads
    ##  update editor
    ##  add color to pad
    ################################################
    def load_voice(self, file_list: list):
        if len(file_list) == 1:
            self.load_audio_voice_to_pad(str(file_list[0]), self.__selected_pad_index)
            self.update_editor_waveform(self.__selected_pad_index)
            self.__pads_module.pad_matrix_list[self.__selected_pad_index].has_content = True
        else:
            for i in range(len(file_list)):
                self.load_audio_voice_to_pad(str(file_list[i]),
                                             (self.__selected_pad_index + i) % len(self.__pads_module.pad_matrix_list))
                self.__pads_module.pad_matrix_list[self.__selected_pad_index + i].has_content = True

            self.update_editor_waveform(self.__selected_pad_index)
            self.__pads_module.refresh_pads()

    def load_audio_voice_to_pad(self, file, pad_index):
        filename = file.split('\\')
        filename = filename[-1]
        self.__filenames_list[pad_index] = filename
        voice: AudioVoice = AudioVoice(file)
        self.__pad_voices_list[pad_index] = voice
        audio_channel = AudioChannel(pad_index, voice, volume=1.0, pan_scaled=0.5)
        self.__audio_channels_list[pad_index] = audio_channel
        self.__sound_engine.update_audio_channels(self.__audio_channels_list)

    def update_editor_waveform(self, index):
        voice = self.__pad_voices_list[index]
        data = voice.original_voice_data
        channel_vol = self.__audio_channels_list[index].volume
        channel_pan = self.__audio_channels_list[index].pan_scaled
        self.__sample_editor.waveform_widget.sample_data = data
        self.__sample_editor.filename = self.__filenames_list[index]
        self.__selected_pad_index = index

        # set dials
        self.__sample_editor.start_pos_dial = voice.sample_start_scaling
        self.__sample_editor.end_pos_dial = voice.sample_end_scaling

        # get pitch of voice
        self.__sample_editor.pitch_dial = voice.pitch_factor
        self.__sample_editor.stretch_dial = voice.stretch_factor

        self.__sample_editor.volume_dial = channel_vol
        self.__sample_editor.pan_dial = channel_pan

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
        self.__app_midi.stop_inport()
        self.__app_midi.open_inport()

    def __reset_application(self):
        reply = QMessageBox.question(
            self,
            "Reset Drum Pads",
            "Press ok to reset",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Ok:
            self.restart_requested_signal.emit()  # Emit the signal
        else:
            print("User canceled restart.")

    @property
    def sound_engine(self):
        return self.__sound_engine

    @property
    def drum_pad_app(self):
        return self
