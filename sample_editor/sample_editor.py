from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QDial, QGridLayout, QGroupBox, QWidget, QPushButton

from sample_editor.waveform_widget import WaveFormWidget


class SampleEditor(QWidget):
    def __init__(self, sample_data, filename=""):
        super().__init__()
        self.__sample_data = sample_data
        self.__start_position = 0
        self.__end_position = 0
        self.__sample_pitch = 0.0
        self.__sample_stretch = 0.0
        self.__filename = filename

        self.__btn__load_sample = QPushButton("Load")

        self.__lbl_start = QLabel('start')
        self.__dial_start = QDial()

        self.__lbl_end = QLabel('end')
        self.__dial_end = QDial()

        self.__lbl_pitch = QLabel('pitch')
        self.__dial_pitch = QDial()

        self.__lbl_stretch = QLabel('stretch')
        self.__dial_stretch = QDial()

        self.__lbl_channel_controls = QLabel('channel')

        self.__lbl_volume = QLabel('vol')
        self.__dial_volume = QDial()

        self.__lbl_pan = QLabel('pan')
        self.__dial_pan = QDial()

        self.__lbl_file_name = QLabel('filename: ')
        self.__lbl_file_name_text = QLabel('')

        self.__waveform_widget = WaveFormWidget(sample_data, 300, 140, 0, 0)
        self.__waveform_widget.setGeometry(100, 100, 800, 200)

        self.__lbl_blank = QLabel()

        sample_control_layout = QGridLayout()
        sample_control_layout.addWidget(self.__btn__load_sample, 0, 0, 1, 1)
        sample_control_layout.addWidget(self.__lbl_blank, 0, 1, 1, 1)

        sample_control_layout.addWidget(self.__lbl_start, 0, 2, 1, 1)
        sample_control_layout.addWidget(self.__dial_start, 0, 3, 1, 1)
        sample_control_layout.addWidget(self.__lbl_blank, 0, 4, 1, 1)

        sample_control_layout.addWidget(self.__lbl_end, 0, 5, 1, 1)
        sample_control_layout.addWidget(self.__dial_end, 0, 6, 1, 1)
        sample_control_layout.addWidget(self.__lbl_blank, 0, 7, 1, 1)

        sample_control_layout.addWidget(self.__lbl_pitch, 0, 8, 1, 1)
        sample_control_layout.addWidget(self.__dial_pitch, 0, 9, 1, 1)
        sample_control_layout.addWidget(self.__lbl_blank, 0, 10, 1, 1)

        sample_control_layout.addWidget(self.__lbl_stretch, 0, 11, 1, 1)
        sample_control_layout.addWidget(self.__dial_stretch, 0, 12, 1, 1)

        channel_control_layout = QGridLayout()
        channel_control_layout.addWidget(self.__lbl_file_name_text, 0, 0, 1, 1)
        channel_control_layout.addWidget(self.__lbl_blank, 0, 1, 1, 2)
        channel_control_layout.addWidget(self.__lbl_volume, 0, 3, 1, 1, Qt.AlignmentFlag.AlignRight)
        channel_control_layout.addWidget(self.__dial_volume, 0, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
        channel_control_layout.addWidget(self.__lbl_blank, 0, 5, 1, 1)
        channel_control_layout.addWidget(self.__lbl_pan, 0, 6, 1, 1, Qt.AlignmentFlag.AlignRight)
        channel_control_layout.addWidget(self.__dial_pan, 0, 7, 1, 1, Qt.AlignmentFlag.AlignLeft)
        channel_control_layout.addWidget(self.__lbl_blank, 0, 8, 1, 6)

        waveform_layout = QGridLayout()
        waveform_layout.addWidget(self.__waveform_widget, 0, 0)

        filename_layout = QGridLayout()
        filename_layout.addWidget(self.__lbl_file_name_text, 0, 0, 1, 3)

        group_box = QGroupBox('Editor')
        editor_layout = QGridLayout()
        editor_layout.addLayout(sample_control_layout, 0, 0, 1, 1)
        editor_layout.addLayout(channel_control_layout, 1, 0, 1, 1)
        editor_layout.addLayout(waveform_layout, 2, 0, 5, 4)

        group_box.setLayout(editor_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        self.__set_style()

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
            self.__lbl_start, self.__lbl_end, self.__lbl_pitch, self.__lbl_stretch, self.__lbl_file_name_text,
            self.__lbl_volume, self.__lbl_pan, self.__lbl_channel_controls
        ]:
            lbl.setStyleSheet(label_style)

        for dial in [
            self.__dial_start, self.__dial_end, self.__dial_pitch, self.__dial_stretch,
            self.__dial_volume, self.__dial_pan
        ]:
            dial.setMinimum(0)
            dial.setMaximum(100)
            dial.setValue(0)
            dial.setFixedSize(25, 25)
            dial.setNotchesVisible(False)
            dial.setWrapping(False)

            if dial in [self.__dial_pitch, self.__dial_stretch, self.__dial_volume, self.__dial_pan]:
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

    @property
    def filename(self):
        return self.__lbl_file_name_text.text()

    @filename.setter
    def filename(self, value):
        self.__lbl_file_name_text.setText(value)

    @property
    def volume_dial(self):
        return self.__dial_volume

    @volume_dial.setter
    def volume_dial(self, value):
        self.__dial_volume.setValue(int(value * 100))

    @property
    def pan_dial(self):
        return self.__dial_pan

    @pan_dial.setter
    def pan_dial(self, value):
        self.__dial_pan.setValue(int(value * 100))
