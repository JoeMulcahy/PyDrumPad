from PyQt6.QtWidgets import QWidget, QGridLayout

from drum_pads.drum_pads_module import DrumPadModule
from globals_controls.globals_settings_module import GlobalControls
from midi.app_midi import AppMidi
from sample_editor.sample_view import SampleViewer
from sound_engine.SynthVoice import SynthVoice


class DrumPadApp(QWidget):
    def __init__(self):
        super().__init__()

        self.__app_layout = QGridLayout()
        self.__pads = DrumPadModule()
        self.__global_controls = GlobalControls()

        test_sample = self.__pads.pad_voices[89].voice_data

        self.__sample_view = SampleViewer(test_sample)

        self.__app_layout.addWidget(self.__pads, 0, 0, 4, 4)
        self.__app_layout.addWidget(self.__global_controls, 0, 4, 1, 3)
        self.__app_layout.addWidget(self.__sample_view, 1, 4, 3, 3)

        self.setLayout(self.__app_layout)

        self.__app_midi = AppMidi()

        # populate global_controls.device.combobox with available devices
        self.__global_controls.device_combo_box.addItems(self.__app_midi.ports_list)

        # global_controls.device.combobox listener
        self.__global_controls.device_combo_box.currentIndexChanged.connect(self.__change_port)

        # signal listeners
        self.__app_midi.mm_signal_note_on.connect(lambda on, note, vel: self.midi_trigger_note_on(on, note, vel))
        self.__app_midi.mm_signal_note_off.connect(lambda on, note: self.midi_trigger_note_off(on, note))
        self.__app_midi.mm_signal_cc.connect(lambda cc, value: self.midi_trigger_cc(cc, value))

        # listener for pads
        for i, btn in enumerate(self.__pads.pad_list):
            button = btn.button
            button.pressed.connect(lambda index=i: self.update_editor_waveform(index))

        # listener for wave_viewer load sample button
        self.__sample_view.load_sample_button.clicked.connect(lambda: self.__load_sample())

    def __load_sample(self):
        index = self.__pads.current_selected_pad
        # self.__pads.pad_list[index].
        print(f'pad index for load: {index}')

    def update_editor_waveform(self, index):
        self.__sample_view.waveform_widget.sample_data = self.__pads.pad_voices[index].voice_data
        print(f'editor waveform: {index}')
        self.repaint()

    def midi_trigger_note_on(self, on, note, velocity):
        index = (note - 36) + 32
        self.__pads.trigger_pad(index)
        self.__pads.highlight_selected(index)

    def midi_trigger_note_off(self, off, note):
        pass
        # print(f'midi off: {off} {note}')

    def midi_trigger_cc(self, cc, value):
        pass
        # print(f'midi cc: {cc} {value}')

    def __change_port(self, index):
        self.__app_midi.select_midi_port(index)
        self.__app_midi.open_inport()
