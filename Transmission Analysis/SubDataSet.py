import os

from Utils import get_number_from_file_name
from Power import Power

class SubDataSet():

    def __init__(self, data_set, path, name):
        self.data_set = data_set
        self.path = path
        self.name = name

    def set_power_objects(self):
        self.files = os.listdir(self.path)
        power_file_names_dict = self.get_power_file_names_dict()
        self.power_objects = [Power(self, power, file_names)
                              for power, file_names in power_file_names_dict.items()]

    def get_power_file_names_dict(self):
        file_name_powers = self.get_file_name_powers()
        power_file_names_dict = self.get_empty_power_file_names_dict(file_name_powers)
        power_file_names_dict = self.fill_power_file_names_dict(power_file_names_dict, file_name_powers)
        return power_file_names_dict

    def get_file_name_powers(self):
        file_name_powers = {file_name: get_number_from_file_name("power", file_name, number_type=int)
                            for file_name in self.files}
        return file_name_powers

    def get_empty_power_file_names_dict(self, file_name_powers):
        powers = sorted(list(set(powers for powers in file_name_powers.values())))
        power_file_names_dict = {power: [] for power in powers}
        return power_file_names_dict

    def fill_power_file_names_dict(self, power_file_names_dict, file_name_powers):
        for file_name, power in file_name_powers.items():
            power_file_names_dict[power].append(file_name)
        return power_file_names_dict
    
    def read_raw_transmission(self):
        for power_obj in self.power_objects:
            power_obj.read_raw_transmission()

    def plot_transmission(self, option, group_size):
        for power_obj in self.power_objects:
            power_obj.plot_transmission(option, group_size)
    
    def align_transmission(self, group_size):
        for power_obj in self.power_objects:
            power_obj.align_transmission(group_size)

    def __str__(self):
        if self.data_set.folder_structure_type == 1:
            string = self.get_string_1()
        else:
            string = self.get_string_2()
        return string

    def get_string_1(self):
        string = (f"{self.name}")
        return string

    def get_string_2(self):
        string = (f"{self.data_set.folder_name}, {self.name}")
        return string
