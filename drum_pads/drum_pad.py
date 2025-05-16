from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QSizePolicy, QVBoxLayout


class DrumPad(QWidget):
    _pad_id = 0

    def __init__(self, midi_number, pad_text_note="", pad_file_text="", width=60, height=60, has_content=False):
        super().__init__()
        self.__btn_pad = QPushButton()
        self.__id = DrumPad._pad_id
        self.__midi_number = midi_number
        self.__width = width
        self.__height = height
        self.__pad_text_note = pad_text_note
        self.__pad_text_note = pad_file_text

        self.__is_selected = False
        self.__has_content = has_content

        self.__btn_pad.setFixedSize(width, height)
        self.__btn_pad.setText(pad_text_note)

        self.__size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(self.__size_policy)

        self.__drum_pad_default_style = \
            """
                    QPushButton{
                        font-size: 8px;
                        color: #7f8781;
                        background-color: #2b2e2c;
                        text-align: top center;
                    }
                """
        self.__drum_pad_selected_style = \
            """
                QPushButton { 
                    border: 2px solid #ff2233; 
                    font-size: 8px;
                    color: #ffffff;
                    background-color: #5522ff;
                    text-align: top center;
                }
            """

        self.__drum_pad_content_style = \
            """
                QPushButton { 
                    font-size: 8px;
                    color: #ffffff;
                    background-color: #456e46;
                    text-align: top center;
                }
            """

        if has_content:
            self.__btn_pad.setStyleSheet(self.__drum_pad_content_style)
        else:
            self.__btn_pad.setStyleSheet(self.__drum_pad_default_style)

        layout = QVBoxLayout()
        layout.addWidget(self.__btn_pad)
        self.setLayout(layout)

        DrumPad._pad_id += 1

    def select(self):
        self.__is_selected = True
        self.__btn_pad.setStyleSheet(self.__drum_pad_selected_style)

    def unselect(self):
        self.__is_selected = False
        if self.__has_content:
            self.__btn_pad.setStyleSheet(self.__drum_pad_content_style)
        else:
            self.__btn_pad.setStyleSheet(self.__drum_pad_default_style)

    @property
    def button(self):
        return self.__btn_pad

    @property
    def pad_id(self):
        return self.__id

    @property
    def midi_number(self):
        return self.__midi_number

    @midi_number.setter
    def midi_number(self, value):
        self.__midi_number = value

    @property
    def pad_text(self):
        return self.__pad_text_note

    @pad_text.setter
    def pad_text(self, value):
        self.__pad_text_note = value

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.__height = value

    @property
    def has_content(self):
        return self.__has_content

    @has_content.setter
    def has_content(self, value):
        self.__has_content = value
