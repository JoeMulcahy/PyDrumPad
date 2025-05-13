from PyQt6.QtGui import QColor, QPen, QPainter
from PyQt6.QtWidgets import QWidget
import sys
import numpy as np


class WaveFormWidget(QWidget):
    def __init__(self, sample_data, width, height, start, end, parent=None):
        super().__init__()
        self.__sample_data = sample_data

        self.__wave_color = QColor(0, 120, 215)
        self.__start_color = QColor(183, 235, 52)
        self.__end_color = QColor(235, 52, 52)

        self.__pen = QPen(self.__wave_color, 1)

        self.__width = width
        self.__height = height
        self.__start_pos = 0
        self.__end_pos = self.__width

    def paintEvent(self, event):
        painter = QPainter(self)

        width = self.__width
        height = self.__height
        num_samples = len(self.__sample_data)
        max_amplitude = 0

        if num_samples > 0:
            max_amplitude = np.max(np.abs(self.__sample_data))
            if max_amplitude == 0:
                return

        # Calculate the scaling factor to fit the waveform within the widget height
        scale_factor = height / (2 * max_amplitude)

        # Calculate the step size for drawing
        step = max(1, num_samples // width)  # Ensure at least one sample per pixel

        # Iterate through the width and draw lines between consecutive (scaled) data points
        self.__pen = QPen(self.__wave_color, 1)
        painter.setPen(self.__pen)

        for i in range(width - 1):
            index1 = int(i * step)
            index2 = int((i + 1) * step)

            if index2 < num_samples:
                x1 = i
                y1 = height / 2 - self.__sample_data[index1] * scale_factor
                x2 = i + 1
                y2 = height / 2 - self.__sample_data[index2] * scale_factor
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # draw start line
        self.__pen = QPen(self.__start_color, 2)
        painter.setPen(self.__pen)
        painter.drawLine(self.__start_pos, 0, self.__start_pos, self.__height)

        # draw end line
        self.__pen = QPen(self.__end_color, 2)
        painter.setPen(self.__pen)
        painter.drawLine(self.__end_pos - 2, 0, self.__end_pos - 2, self.__height)



    @property
    def start_position(self):
        return self.__start_pos

    @start_position.setter
    def start_position(self, value):
        self.__start_pos = int(self.__width * value)

    @property
    def end_position(self):
        return self.__end_pos

    @end_position.setter
    def end_position(self, value):
        self.__end_pos = int(self.__width - (self.__width * value))

    @property
    def sample_data(self):
        return self.__sample_data

    @sample_data.setter
    def sample_data(self, value):
        self.__sample_data = value


