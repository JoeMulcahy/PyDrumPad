from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton

import utility.music_notes as mn
from drum_pads.drum_pad import DrumPad


class DrumPadModule(QWidget):
    def __init__(self):
        super().__init__()
        self.__midi_notes_dict: dict = mn.MIDI_NOTE_NUMBER_TO_MUSIC_NOTE_DICT
        self.__bank_index = 0
        self.__pad_matrix_list = []
        self.__currently_selected_pad_index = 0
        self.__bank_buttons_list = []

        self.__bank_btn_default_style = ""
        self.__bank_btn_selected_style = "QPushButton { background-color: #aeb853}"

        # initialise bank buttons and add to bank_buttons_layout
        bank_buttons_layout = QGridLayout()
        for i in range(0, 6):
            btn = QPushButton(f'{i + 1}')
            btn.setFixedSize(30, 30)
            self.__bank_buttons_list.append(btn)
            bank_buttons_layout.addWidget(btn, 0, i, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.__pads_layout = QGridLayout()
        self.__pads_layout.setSpacing(1)

        # create drum pads and add to pad_matrix_list
        for i in range(len(mn.MIDI_NOTE_NUMBERS_LIST)):
            midi_note = mn.MIDI_NOTE_NUMBERS_LIST[i]
            music_note = mn.MUSIC_NOTES_LIST[i]
            pad = DrumPad(midi_note, music_note)
            self.__pad_matrix_list.append(pad)

        self.__update_visible_pads()  # display current bank of pads and add to self.__pads_layout

        group_box = QGroupBox('Pads')  # group box for pads matrix

        module_layout = QGridLayout()
        module_layout.addLayout(bank_buttons_layout, 0, 0, )
        module_layout.addLayout(self.__pads_layout, 1, 0)

        group_box.setLayout(module_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        self.__update_bank_of_pads(self.__bank_index)  # initial bank to display

        # listeners for bank buttons
        for i in range(len(self.__bank_buttons_list)):
            button = self.__bank_buttons_list[i]
            button.clicked.connect(lambda clicked, index=i: self.__update_bank_of_pads(index))

    #############################################
    ## update which bank of pads are visible
    #############################################
    def __update_bank_of_pads(self, index):
        for btn in self.__bank_buttons_list:
            btn.setStyleSheet(self.__bank_btn_default_style)

        self.__bank_buttons_list[index].setStyleSheet(self.__bank_btn_selected_style)

        self.__bank_index = index
        self.__clear_grid_layout()
        self.__update_visible_pads()

    def __update_visible_pads(self):
        visible_pads = []
        for i in range(0, 16):
            visible_pads.append(self.__pad_matrix_list[self.__bank_index * 16 + i])

        for row in range(0, 4):
            for col in range(0, 4):
                pad = visible_pads[row * 4 + col]
                self.__pads_layout.addWidget(pad, 3 - row, col, 1, 1, Qt.AlignmentFlag.AlignCenter)

    def __clear_grid_layout(self):
        while self.__pads_layout.count():
            item = self.__pads_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_grid_layout(sub_layout)  # Recursively clear nested layouts

    def refresh_pads(self):
        for pad in self.__pad_matrix_list:
            pad.unselect()



    @property
    def drum_pads_module(self):
        return self

    @property
    def pad_matrix_list(self):
        return self.__pad_matrix_list

    @property
    def current_selected_pad_index(self):
        return self.__currently_selected_pad_index

    @property
    def bank_index(self):
        return self.__bank_index
