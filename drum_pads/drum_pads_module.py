from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton

from drum_pad import DrumPad
import utility.music_notes as mn


class DrumPadModule(QWidget):
    def __init__(self):
        super().__init__()
        self.__midi_notes_dict: dict = mn.MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT
        self.__bank_index = 3
        self.__pads_visible_list = []
        self.__bank_buttons_list = []
        self.__pad_voices = []

        bank_buttons_layout = QGridLayout()
        for i in range(0, 6):
            btn = QPushButton(f'{i + 1}')
            btn.setFixedSize(30, 30)
            self.__bank_buttons_list.append(btn)
            bank_buttons_layout.addWidget(btn, 0, i, 1, 1, Qt.AlignmentFlag.AlignCenter)

        pads_layout = QGridLayout()
        pads_layout.setSpacing(1)
        # 4 x 4 pads
        for row in range(0, 4):
            for col in range(0, 4):
                num = row * 4 + col
                key = 60 + num
                note = self.__midi_notes_dict[key]
                pad = DrumPad(60 + num, note)
                self.__pads_visible_list.append(pad)
                pads_layout.addWidget(pad, 4 - row, col, 1, 1, Qt.AlignmentFlag.AlignCenter)

        group_box = QGroupBox('Pads')

        module_layout = QGridLayout()
        module_layout.addLayout(bank_buttons_layout, 0, 0, )
        module_layout.addLayout(pads_layout, 1, 0)

        group_box.setLayout(module_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        # listeners for bank buttons
        for i in range(len(self.__bank_buttons_list)):
            button = self.__bank_buttons_list[i]
            button.clicked.connect(lambda clicked, index=i: self.__set_bank_index(index))

        # listener for pads
        for i, btn in enumerate(self.__pads_visible_list):
            button = btn.button
            button.clicked.connect(lambda clicked, index=i: self.__highlight_selected(index))

    def __highlight_selected(self, index):
        for pad in self.__pads_visible_list:
            pad.unselect()

        self.__pads_visible_list[index].select()

    def __set_bank_index(self, index):
        self.__bank_index = index

    def __update_visible_pads(self):
        pass

