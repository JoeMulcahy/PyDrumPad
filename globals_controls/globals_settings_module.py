from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QComboBox, QDial, QSizePolicy, QGroupBox


class GlobalControls(QWidget):
    def __init__(self):
        super().__init__()

        self.__size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.__lbl__device = QLabel("Device")
        self.__combo_device = QComboBox()

        self.__lbl_preset = QLabel('Preset')
        self.__btn_load_preset = QPushButton('Load')
        self.__btn_save_preset = QPushButton('Save')

        self.__lbl_reset = QLabel('Reset')
        self.__btn_reset = QPushButton('Reset')

        self.__dial_volume = QDial()
        self.__lbl_volume = QLabel('Volume')

        self.__set_style()  # set styling for widgets

        self.__settings_layout = QGridLayout()
        self.__settings_layout.addWidget(self.__lbl__device, 0, 0, 1, 2)
        self.__settings_layout.addWidget(self.__combo_device, 0, 1, 1, 2)

        self.__settings_layout.addWidget(self.__lbl_preset, 1, 0, 1, 1)
        self.__settings_layout.addWidget(self.__btn_load_preset, 1, 1, 1, 1)
        self.__settings_layout.addWidget(self.__btn_save_preset, 1, 2, 1, 1)

        self.__settings_layout.addWidget(self.__lbl_reset, 2, 0, 1, 1)
        self.__settings_layout.addWidget(self.__btn_reset, 2, 1, 1, 1)

        self.__settings_layout.addWidget(self.__dial_volume, 0, 3, 2, 2)
        self.__settings_layout.addWidget(self.__lbl_volume, 1, 3, 1, 2)

        self.__groupbox = QGroupBox("Global Controls")
        self.__groupbox.setLayout(self.__settings_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(self.__groupbox)
        self.setLayout(main_layout)

    def __set_style(self):
        pass

    @property
    def global_controls_module(self):
        return self

    @property
    def volume_dial(self):
        return self.__dial_volume

    @property
    def load_preset_btn(self):
        return self.__btn_load_preset

    @property
    def save_preset_btn(self):
        return self.__btn_save_preset

    @property
    def reset_preset_btn(self):
        return self.__btn_reset

    @property
    def device_combo_box(self):
        return self.__combo_device
