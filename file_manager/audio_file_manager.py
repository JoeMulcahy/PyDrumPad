from pathlib import Path
from tkinter import filedialog

from PyQt6.QtCore import QObject, pyqtSignal, QThread
import tkinter as tk

from settings import Settings


class LoadFilesFromDirectoryWorker(QObject):
    """
        :param
        directory: str
        extension: list of extension

        :return
        signal: list of files

    """
    files_list_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, directory: Path, mode='dir', extension: list = None):
        super().__init__()
        self.directory = directory
        self.extension = extension
        self.file_mode = mode

    def run(self):
        file_list = []
        file_paths = []
        if self.file_mode == 'dir':
            if not self.directory.is_dir():
                self.error_signal.emit(f"{self.directory} is not a valid directory!")
                print(f"{self.directory} is not a valid directory!")
                return

            try:
                for file in self.directory.iterdir():
                    if file.is_file():
                        if not self.extension:
                            file_path = str(self.directory) + '\\' + file.name
                            file_paths.append(file_path)
                        elif file.suffix in self.extension:
                            file_list.append(file)
                            file_paths.append(file_path)

                self.files_list_signal.emit(file_paths)

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.error_signal.emit(f"Error when scanning directory: {e}")
                print(f"Error when scanning directory: {e}")
        else:
            try:
                with open(self.directory) as file:
                    file_path = str(self.directory)
                    file_paths.append(file_path)
                    self.files_list_signal.emit(file_paths)
            except FileNotFoundError:
                print(f"Error: File not found at '{self.directory}'")
                self.files_list_signal.emit([])
            except Exception as e:
                print(f"An error occurred: {e}")
                self.files_list_signal.emit([])


class FileManager(QObject):
    files_loaded_signal = pyqtSignal(list)
    error_occurred_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._file_list = []
        self.__thread = None
        self.__worker = None

    def get_files_list_from_directory(self, directory, mode='dir', extension: list = None):
        path_object = Path(directory)
        self.__thread = QThread(self)

        self.__worker = LoadFilesFromDirectoryWorker(path_object, mode, extension)

        self.__worker.moveToThread(self.__thread)
        self.__thread.started.connect(self.__worker.run)
        self.__worker.files_list_signal.connect(lambda l: self._handle_file_list(l))
        self.__worker.error_signal.connect(self.error_occurred_signal)
        self.__thread.finished.connect(self.__thread.deleteLater)
        # _worker.finished.connect(_worker.deleteLater)

        self.__thread.start()

    def _handle_file_list(self, list_of_files: list):
        if list_of_files:
            self.files_loaded_signal.emit(list_of_files)
        else:
            print('No files found')
            self.files_loaded_signal.emit([])

    def get_files_using_explorer(self, mode='directory'):
        root = tk.Tk()
        root.withdraw()  # Hide main window

        if mode == 'directory':
            path = filedialog.askdirectory(
                initialdir=Settings.DEFAULT_DIR,
                title="Choose .wav files in directory"
            )
            self.get_files_list_from_directory(Path(path), mode='dir')
        else:
            path = filedialog.askopenfilename(
                initialdir=Settings.DEFAULT_DIR,
                title="Choose a file"
                # filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
            )
            # print(f'single: {path}')
            self.get_files_list_from_directory(Path(path), mode='single')

