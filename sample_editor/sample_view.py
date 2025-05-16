from PyQt6.QtWidgets import QLabel, QDial, QGridLayout, QGroupBox, QWidget, QPushButton

from sample_editor.waveform_widget import WaveFormWidget


class SampleEditor(QWidget):
    def __init__(self, sample_data):
        super().__init__()
        self.__sample_data = sample_data
        self.__start_position = 0
        self.__end_position = 0
        self.__sample_pitch = 0.0
        self.__sample_stretch = 0.0

        self.__btn__load_sample = QPushButton("Load")

        self.__lbl_start = QLabel('start')
        self.__dial_start = QDial()

        self.__lbl_end = QLabel('end')
        self.__dial_end = QDial()

        self.__lbl_pitch = QLabel('pitch')
        self.__dial_pitch = QDial()

        self.__lbl_stretch = QLabel('stretch')
        self.__dial_stretch = QDial()

        self.__waveform_widget = WaveFormWidget(sample_data, 300, 180, 0, 0)
        self.__waveform_widget.setGeometry(100, 100, 800, 200)

        self.__lbl_blank = QLabel()

        control_layout = QGridLayout()
        control_layout.addWidget(self.__btn__load_sample, 0, 0, 1, 1)
        control_layout.addWidget(self.__lbl_blank, 0, 1, 1, 1)

        control_layout.addWidget(self.__lbl_start, 0, 2, 1, 1)
        control_layout.addWidget(self.__dial_start, 0, 3, 1, 1)
        control_layout.addWidget(self.__lbl_blank, 0, 4, 1, 1)

        control_layout.addWidget(self.__lbl_end, 0, 5, 1, 1)
        control_layout.addWidget(self.__dial_end, 0, 6, 1, 1)
        control_layout.addWidget(self.__lbl_blank, 0, 7, 1, 1)

        control_layout.addWidget(self.__lbl_pitch, 0, 8, 1, 1)
        control_layout.addWidget(self.__dial_pitch, 0, 9, 1, 1)
        control_layout.addWidget(self.__lbl_blank, 0, 10, 1, 1)

        control_layout.addWidget(self.__lbl_stretch, 0, 11, 1, 1)
        control_layout.addWidget(self.__dial_stretch, 0, 12, 1, 1)

        self.__set_style()

        waveform_layout = QGridLayout()
        waveform_layout.addWidget(self.__waveform_widget, 0, 0)

        group_box = QGroupBox('Editor')
        editor_layout = QGridLayout()
        editor_layout.addLayout(control_layout, 0, 0, 1, 1)
        editor_layout.addLayout(waveform_layout, 1, 0, 1, 1)

        group_box.setLayout(editor_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        # listeners
        self.__dial_start.valueChanged.connect(lambda val: self.__change_sample_start(val / 100))
        self.__dial_end.valueChanged.connect(lambda val: self.__change_sample_end(val / 100))

    def __change_sample_start(self, val):
        self.waveform_widget.start_position = val
        self.repaint()

    def __change_sample_end(self, val):
        self.waveform_widget.end_position = val
        self.repaint()

    def __set_style(self):
        button_style = "QPushButton { font-size: 8px}"
        self.__btn__load_sample.setFixedSize(30, 25)
        self.__btn__load_sample.setStyleSheet(button_style)

        label_style = "QLabel { font-size: 8px}"

        for lbl in [
            self.__lbl_start, self.__lbl_end, self.__lbl_pitch, self.__lbl_stretch
        ]:
            lbl.setStyleSheet(label_style)

        for dial in [
            self.__dial_start, self.__dial_end, self.__dial_pitch, self.__dial_stretch
        ]:
            dial.setMinimum(0)
            dial.setMaximum(100)
            dial.setValue(0)
            dial.setFixedSize(25, 25)
            dial.setNotchesVisible(False)
            dial.setWrapping(False)

            if dial in [self.__dial_pitch, self.__dial_stretch]:
                dial.setValue(50)

    @property
    def waveform_widget(self):
        return self.__waveform_widget

    @property
    def load_sample_button(self):
        return self.__btn__load_sample

    @property
    def start_pos_dial(self):
        return self.__dial_start

    @start_pos_dial.setter
    def start_pos_dial(self, value):
        self.__dial_start.setValue(int(value * 100))
        self.__change_sample_start(value)

    @property
    def end_pos_dial(self):
        return self.__dial_end

    @end_pos_dial.setter
    def end_pos_dial(self, value):
        self.__dial_end.setValue(int(value * 100))
        self.__change_sample_end(value)

    @property
    def pitch_dial(self):
        return self.__dial_pitch

    @pitch_dial.setter
    def pitch_dial(self, value):
        self.__dial_pitch.setValue(int(value * 100))

    @property
    def stretch_dial(self):
        return self.__dial_stretch

    @stretch_dial.setter
    def stretch_dial(self, value):
        self.__dial_stretch.setValue(int(value * 100))
