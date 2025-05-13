from PyQt6.QtWidgets import QWidget, QGridLayout

from drum_pads.drum_pads_module import DrumPadModule
from globals_controls.globals_settings_module import GlobalControls
from midi.app_midi import AppMidi


class DrumPadApp(QWidget):
    def __init__(self):
        super().__init__()

        self.__app_layout = QGridLayout()
        self.__pads = DrumPadModule()
        self.__global_controls = GlobalControls()

        self.__app_layout.addWidget(self.__pads, 0, 0, 1, 1)
        self.__app_layout.addWidget(self.__global_controls, 0, 1, 1, 1)

        self.setLayout(self.__app_layout)

        self.__app_midi = AppMidi()
        self.__app_midi.select_midi_port(2)

        # populate global_controls.device.combobox with available devices
        self.__global_controls.device_combo_box.addItems(self.__app_midi.ports_list)

        # global_controls.device.combobox listener
        self.__global_controls.device_combo_box.currentIndexChanged.connect(self.__change_port)

        # signal listeners
        self.__app_midi.mm_signal_note_on.connect(lambda on, note, vel: self.midi_trigger_note_on(on, note, vel))
        self.__app_midi.mm_signal_note_off.connect(lambda on, note: self.midi_trigger_note_off(on, note))
        self.__app_midi.mm_signal_cc.connect(lambda cc, value: self.midi_trigger_cc(cc, value))

    def midi_trigger_note_on(self, on, note, velocity):
        index = (note - 36) + 32
        print(f'midi on: {on} {note} {velocity}')
        self.__pads.trigger_pad(index)
        self.__pads.highlight_selected(index)

    def midi_trigger_note_off(self, off, note):
        print(f'midi off: {off} {note}')

    def midi_trigger_cc(self, cc, value):
        print(f'midi cc: {cc} {value}')

    def __change_port(self, index):
        self.__app_midi.select_midi_port(index)
        self.__app_midi.open_inport()
