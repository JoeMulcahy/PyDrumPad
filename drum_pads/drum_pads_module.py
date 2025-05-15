from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton

from app_enums.wave_form_enum import WaveForm
from drum_pads.drum_pad import DrumPad
import utility.music_notes as mn
from sound_engine.AudioChannel import AudioChannel
from sound_engine.AudioVoice import AudioVoice
from sound_engine.SoundEngine import SoundEngine
from sound_engine.SynthVoice import SynthVoice


class DrumPadModule(QWidget):
    def __init__(self):
        super().__init__()
        self.__midi_notes_dict: dict = mn.MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT
        self.__bank_index = 3
        self.__pads_list = []
        self.__currently_selected_pad_index = 0
        self.__bank_buttons_list = []
        self.__pad_voices_list = []
        self.__audio_channels_list = []

        self.__bank_btn_default_style = ""
        self.__bank_btn_selected_style = "QPushButton { background-color: #999999}"

        # initialise sound engine and audio channels
        self.__sound_engine = SoundEngine()
        self.__pad_voices_list = self.__create_pad_voices()
        self.__audio_channels_list = self.__create_audio_channels()
        self.__add_channels_to_engine()

        self.test_list_voice()

        # banks initialisation
        bank_buttons_layout = QGridLayout()
        for i in range(0, 6):
            btn = QPushButton(f'{i + 1}')
            btn.setFixedSize(30, 30)
            self.__bank_buttons_list.append(btn)
            bank_buttons_layout.addWidget(btn, 0, i, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.__pads_layout = QGridLayout()
        self.__pads_layout.setSpacing(1)

        # create pads list
        for i in range(len(mn.MIDI_NOTE_NUMBERS_LIST)):
            midi_note = mn.MIDI_NOTE_NUMBERS_LIST[i]
            music_note = mn.MUSIC_NOTES_LIST[i]
            pad = DrumPad(midi_note, music_note)
            self.__pads_list.append(pad)

        # display current pads
        self.__update_visible_pads()

        group_box = QGroupBox('Pads')

        module_layout = QGridLayout()
        module_layout.addLayout(bank_buttons_layout, 0, 0, )
        module_layout.addLayout(self.__pads_layout, 1, 0)

        group_box.setLayout(module_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        self.__set_bank_index(3)
        self.__sound_engine.play()  # active sound engine

        # listeners for bank buttons
        for i in range(len(self.__bank_buttons_list)):
            button = self.__bank_buttons_list[i]
            button.clicked.connect(lambda clicked, index=i: self.__set_bank_index(index))

        # listener for pads
        for i, btn in enumerate(self.__pads_list):
            button = btn.button
            button.clicked.connect(lambda clicked, index=i: self.highlight_selected(index))
            button.pressed.connect(lambda index=i: self.trigger_pad(index))

    def highlight_selected(self, index):
        for pad in self.__pads_list:
            pad.unselect()

        self.__pads_list[index].select()
        self.__currently_selected_pad_index = index

    def trigger_pad(self, index):
        self.__audio_channels_list[index].trigger()

    def __set_bank_index(self, index):
        for btn in self.__bank_buttons_list:
            btn.setStyleSheet(self.__bank_btn_default_style)

        self.__bank_buttons_list[index].setStyleSheet(self.__bank_btn_selected_style)

        self.__bank_index = index
        self.__clear_grid_layout()
        self.__update_visible_pads()
        self.highlight_selected(self.__currently_selected_pad_index)

    def __update_visible_pads(self):
        visible_pads = []
        for i in range(0, 16):
            visible_pads.append(self.__pads_list[self.__bank_index * 16 + i])

        for row in range(0, 4):
            for col in range(0, 4):
                pad = visible_pads[row * 4 + col]
                self.__pads_layout.addWidget(pad, 3 - row, col, 1, 1, Qt.AlignmentFlag.AlignCenter)

    def __clear_grid_layout(self):
        while self.__pads_layout.count():
            item = self.__pads_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)  # Removes the widget from the GUI
            else:
                # If it's a layout or spacer, you might need to handle it differently
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_grid_layout(sub_layout)  # Recursively clear nested layouts

    def __create_pad_voices(self):
        temp_list = []
        for i in range(len(mn.NOTE_FREQUENCIES_LIST)):
            freq = mn.NOTE_FREQUENCIES_LIST[i]
            voice = SynthVoice(WaveForm.TRIANGLE, float(freq), 0.2, 1.0, 44100)
            temp_list.append(voice)

        return temp_list

    def __create_audio_channels(self):
        temp_list = []
        for i in range(len(self.__pad_voices_list)):
            audio_channel = AudioChannel(i, self.__pad_voices_list[i], volume=0.5, pan=0.5)
            temp_list.append(audio_channel)

        return temp_list

    def load_voice_to_pad(self, file, pad_index):
        voice = AudioVoice(file)
        self.__pad_voices_list[pad_index] = voice
        audio_channel = AudioChannel(pad_index, voice, volume=1.0, pan=0.5)
        self.__audio_channels_list[pad_index] = audio_channel
        print('------------------------')
        self.test_list_voice()
        self.__sound_engine.update_audio_channels(self.__audio_channels_list)

    def __add_channels_to_engine(self):
        for channel in self.__audio_channels_list:
            self.__sound_engine.add_channel(channel)

    @property
    def drum_pads_module(self):
        return self

    @property
    def pad_list(self):
        return self.__pads_list

    @property
    def pad_voices(self):
        return self.__pad_voices_list

    @property
    def current_selected_pad(self):
        return self.__currently_selected_pad_index

    @property
    def current_selected_voice(self):
        return self.__pad_voices_list[self.__currently_selected_pad_index]

    def test_list_voice(self):
        for voice in self.__pad_voices_list:
            print(voice)

    @property
    def sound_engine(self):
        return self.__sound_engine
