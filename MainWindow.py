from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout

from drum_pad_app import DrumPadApp
from drum_pads.drum_pads_module import DrumPadModule
from globals_controls.globals_settings_module import GlobalControls


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PyPad')
        self.central_widget = QWidget()

        self.drum_pad_app = DrumPadApp()
        self.layout = QGridLayout()
        self.layout.addWidget(self.drum_pad_app)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)


    @property
    def main_window(self):
        return self
