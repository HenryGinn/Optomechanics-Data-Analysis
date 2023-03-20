import numpy as np
import matplotlib.pyplot as plt

from Fitting import Fitting
from Utils import get_file_contents
from Utils import convert_to_milliwatts
from Utils import get_number_from_file_name

class Transmission():

    def __init__(self, power_obj, file_name, path):
        self.initialise_from_power_object(power_obj)
        self.initialise_path_data(file_name, path)

    def initialise_from_power_object(self, power_obj):
        self.power_obj = power_obj
        self.power = power_obj.power
        self.sub_data_set = power_obj.sub_data_set
        self.data_set = power_obj.data_set

    def initialise_path_data(self, file_name, path):
        self.file_name = file_name
        self.path = path
        self.transmission_number = get_number_from_file_name("count", self.file_name,
                                                            offset=0, number_type=int)

    def read_raw_transmission(self):
        with open(self.path, "r") as file:
            file.readline()
            self.extract_raw_transmission_from_file(file)

    def extract_raw_transmission_from_file(self, file):
        file_contents = get_file_contents(file, self.file_name)
        voltage, self.frequency = file_contents
        self.set_S21_from_voltage(voltage)

    def set_S21_from_voltage(self, voltage):
        voltage = convert_to_milliwatts(voltage)
        self.S21 = voltage / self.power

    def plot_transmission_raw(self):
        plt.plot(self.frequency, self.S21)
        plt.title(self)
        plt.show()

    def set_peak(self):
        self.peak_index = np.argmax(self.S21)
        self.peak_frequency = self.frequency[self.peak_index]
        self.peak_amplitude = self.S21[self.peak_index]

    def __str__(self):
        string = (f"{self.power_obj}, number {self.transmission_number}")
        return string
