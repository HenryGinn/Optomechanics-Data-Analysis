import os

from Transmission import Transmission
from Utils import get_number_from_file_name
from Utils import convert_to_milliwatts

class Power():

    def __init__(self, sub_data_set, power, file_names):
        self.sub_data_set = sub_data_set
        self.process_power_input(power)
        self.file_names = file_names
        self.process_initial_input()
        self.create_transmission_objects()

    def process_power_input(self, power):
        self.power_string = str(power)
        self.power = convert_to_milliwatts(power)

    def process_initial_input(self):
        self.data_set = self.sub_data_set.data_set
        self.sort_file_names()
        self.paths = [os.path.join(self.sub_data_set.path, file_name)
                      for file_name in self.file_names]

    def sort_file_names(self):
        file_count_dict = {file_name: get_number_from_file_name("count", file_name, offset=0, number_type=int)
                           for file_name in self.file_names}
        if None not in file_count_dict.values():
            self.file_names = sorted(self.file_names, key=lambda x: file_count_dict[x])
    
    def output_file_names(self):
        print(f"\nOutputting {len(self.file_names)} file names for {self}")
        for file_name in self.file_names:
            print(file_name)

    def create_transmission_objects(self):
        self.transmission_objects = [Transmission(self, file_name, path)
                                     for file_name, path in zip(self.file_names, self.paths)]

    def read_raw_transmission(self):
        for transmission_obj in self.transmission_objects:
            transmission_obj.read_raw_transmission()

    def plot_transmission(self, option):
        plot_transmission_options = {"Raw": self.plot_transmission_raw,
                                     "Aligned": self.plot_transmission_aligned}
        plot_transmission_options[option]()

    def plot_transmission_raw(self):
        for transmission_obj in self.transmission_objects:
            transmission_obj.plot_transmission_raw()

    def plot_transmission_aligned(self):
        pass

    def align_transmission(self):
        for transmission_obj in self.transmission_objects:
            transmission_obj.set_peak()

    def __str__(self):
        string = (f"{self.sub_data_set}, {self.power_string} dBm")
        return string
