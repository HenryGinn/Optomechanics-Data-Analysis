import os

import numpy as np

from Utils import get_file_contents_from_path
from Utils import convert_to_milliwatts

class Data():

    def __init__(self, group_obj, path):
        self.group_obj = group_obj
        self.path = path
        self.file_name = os.path.basename(path)

    def set_S21_and_frequency_from_file(self):
        file_contents = get_file_contents_from_path(self.path)
        voltage, self.frequency = file_contents
        self.set_S21_from_voltage(voltage)

    def set_S21_from_voltage(self, voltage):
        self.S21 = convert_to_milliwatts(voltage)
        self.S21 /= self.group_obj.drift

    def set_peak(self):
        self.peak_index = np.argmax(self.S21)
        self.peak_frequency = self.frequency[self.peak_index]
        self.peak_amplitude = self.S21[self.peak_index]
