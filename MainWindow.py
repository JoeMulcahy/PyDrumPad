from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout

from drum_pads.drum_pads_module import DrumPadModule


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PyPad')
        self.central_widget = QWidget()
        self.app_layout = QGridLayout()
        self.pads = DrumPadModule()
        self.app_layout.addWidget(self.pads)
        self.central_widget.setLayout(self.app_layout)
        self.setCentralWidget(self.central_widget)
