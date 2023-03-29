import os

import numpy as np

from CombFunction import CombFunction
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class AverageGroups(CombFunction):
    
    name = "Average of Groups"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_commands(self):
        self.commands = {"Save": self.save_data,
                         "Load": self.load_data}

    def set_paths(self):
        self.set_folder_path()
        self.set_file_paths()

    def set_file_paths(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, drift_obj.folder_name)
        drift_obj.average_group_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            path = os.path.join(detuning_obj.drift_obj.average_group_path,
                                f"{detuning_obj.detuning} Hz.txt")
            detuning_obj.average_group_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.align_spectra("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.save_detuning_obj(detuning_obj)

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.average_group_path, "w") as file:
            file.writelines("Frequency (Hz)\tS21 (mW)\n")
            self.save_detuning_data_to_file(detuning_obj, file)

    def save_detuning_data_to_file(self, detuning_obj, file):
        self.set_average_group_data(detuning_obj)
        spectrum_obj = detuning_obj.spectrum_obj
        for frequency, S21 in zip(spectrum_obj.frequency, spectrum_obj.S21):
            file.writelines(f"{frequency}\t{S21}\n")

    def set_average_group_data(self, detuning_obj):
        self.create_spectrum_object(detuning_obj)
        frequency_S21_dict = self.get_frequency_S21_dict(detuning_obj)
        frequency_S21_dict = self.populate_frequency_S21_dict(detuning_obj, frequency_S21_dict)
        self.set_spectrum_attributes_from_frequency_S21_dict(detuning_obj, frequency_S21_dict)

    def create_spectrum_object(self, detuning_obj):
        if not hasattr(detuning_obj, "spectrum_obj"):
            detuning_obj.spectrum_obj = Spectrum(self)

    def get_frequency_S21_dict(self, detuning_obj):
        frequency_S21_dict = {frequency: [] for group_obj in detuning_obj.group_objects
                              for frequency in group_obj.spectrum_obj.frequency}
        return frequency_S21_dict

    def populate_frequency_S21_dict(self, detuning_obj, frequency_S21_dict):
        for group_obj in detuning_obj.group_objects:
            for frequency, S21 in zip(group_obj.spectrum_obj.frequency, group_obj.spectrum_obj.S21):
                frequency_S21_dict[frequency].append(S21)
        return frequency_S21_dict

    def set_spectrum_attributes_from_frequency_S21_dict(self, detuning_obj, frequency_S21_dict):
        detuning_obj.spectrum_obj.frequency = np.array(list(frequency_S21_dict.keys()))
        detuning_obj.spectrum_obj.S21 = np.mean(list(frequency_S21_dict.values()), axis=1)

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.average_group_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def do_load_data(self):
        self.load_data_from_folders()
        self.loaded = True

    def load_data_from_folders(self):
        for drift_obj in self.data_set_obj.drift_objects:
            for detuning_obj in drift_obj.detuning_objects:
                self.load_data_for_detuning_obj(detuning_obj)

    def load_data_for_detuning_obj(self, detuning_obj):
        self.create_spectrum_object(detuning_obj)
        file_contents = get_file_contents_from_path(detuning_obj.average_group_path)
        detuning_obj.spectrum_obj.frequency, detuning_obj.spectrum_obj.S21 = file_contents
