import mido
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QThread


class MidiWorker(QObject):
    midi_message_received = pyqtSignal(object)

    def __init__(self, port):
        super().__init__()
        self.__port = port
        self.__is_running = True
        self.__inport = None

    @pyqtSlot()
    def run(self):
        print("MIDI Worker started.")
        try:
            self.__inport = mido.open_input(self.__port, callback=self.handle_midi)
        except Exception as e:
            print(f"Failed to open MIDI input: {e}")
            return

    def handle_midi(self, msg):
        if not self.__is_running:
            return

        self.midi_message_received.emit(msg)

    def stop(self):
        print("Stopping MIDI Worker.")
        self.__is_running = False
        if self.__inport:
            self.__inport.close()
            self.__inport = None


class AppMidi(QObject):
    mm_signal_note_on = pyqtSignal(bool, int, int)
    mm_signal_note_off = pyqtSignal(bool, int)    # on/off, note value
    mm_signal_cc = pyqtSignal(int, int)     # cc, value

    def __init__(self):
        super().__init__()
        self.__ports_list = []
        self.__selected_port = None
        self.__midi_worker = None
        self.__thread = None

        self.__initialise_midi()

    def select_midi_port(self, index):
        self.__selected_port = self.__ports_list[index]
        print(f'selected port: {self.__selected_port}')

    def __initialise_midi(self):
        ports = mido.get_input_names()
        for i, port in enumerate(ports):
            print(f'ports: {port}')
            self.__ports_list.append(port)

        if not ports:
            print("No midi ports found")
            return

        # default port [2] if it exists
        if len(ports) > 2:
            self.__selected_port = self.__ports_list[2]
        else:
            self.__selected_port = self.__ports_list[0]

    def open_inport(self):
        self.__midi_worker = MidiWorker(self.__selected_port)
        self.__thread = QThread()
        self.__midi_worker.moveToThread(self.__thread)

        self.__thread.started.connect(self.__midi_worker.run)
        self.__thread.finished.connect(self.__midi_worker.deleteLater)

        # Connect signal to your handler method
        self.__midi_worker.midi_message_received.connect(self.process_midi_message)

        self.__thread.start()

    def stop_inport(self):
        if self.__midi_worker:
            self.__midi_worker.stop()
        if self.__thread:
            self.__thread.quit()
            self.__thread.wait()
            self.__thread = None

    def process_midi_message(self, msg):
        # Handle incoming MIDI message safely from the main thread
        if msg.type == 'note_on' and msg.velocity > 0:
            self.mm_signal_note_on.emit(True, msg.note, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            self.mm_signal_note_off.emit(True, msg.note)
        elif msg.type == 'control_change':
            self.mm_signal_cc.emit(msg.control, msg.value)
        else:
            print(f"Other Message  - {msg}")

    @property
    def ports_list(self):
        return self.__ports_list
