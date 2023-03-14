import os
from copy import deepcopy

import numpy as np

from GreekDetuning import GreekDetuning
from Greek import Greek
from Utils import get_file_contents
from Utils import get_last_number_in_file_name

class GreekTrial():

    def __init__(self, trial_obj):
        self.trial = trial_obj
        self.create_greek_objects()

    def create_greek_objects(self):
        self.greek_objects = [GreekDetuning(detuning_obj)
                              for detuning_obj in self.trial.detuning_objects]

    def process_greek(self, average_size):
        self.set_trial_from_file()
        self.create_greek_obj(average_size)
        self.create_greek_file(average_size)

    def create_greek_obj(self, average_size):
        label = self.get_label_from_average_size(average_size)
        self.trial.greek = Greek(self.trial, self, label)
        self.trial.greek.path = self.get_greek_file_path(average_size)

    def create_greek_file(self, average_size):
        with open(self.trial.greek.path, "w") as file:
            file.writelines(f"Detuning\tDrift\tOmega\tGamma\tAmplitude\n")
            file = self.write_greek_to_file(file, average_size)

    def write_greek_to_file(self, file, average_size):
        for greek_obj in self.greek_objects:
            if greek_obj.detuning.valid:
                greek_obj.set_greeks(average_size)
                file = greek_obj.save_greeks(file)
        return file

    def get_greek_file_path(self, average_size):
        greek_file_name = self.get_greek_file_name(self.trial.greek.label)
        parent_path = self.trial.power_obj.data_set.greek_path
        greek_file_path = os.path.join(parent_path, greek_file_name)
        return greek_file_path

    def get_greek_file_name(self, label):
        data_set = self.trial.power_obj.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial = self.trial.trial_number
        file_name = f"{data_set}_Power_{power}_Trial_{trial}_{label}.txt"
        return file_name

    def average_greek(self):
        self.set_greek_files()
        for file_name in self.greek_files:
            if self.file_has_greek_averages(file_name):
                self.do_average_greek(file_name)

    def set_greek_files(self):
        if hasattr(self, "greek_files") is False:
            self.greek_path = self.trial.data_set.greek_path
            self.greek_files = self.trial.get_data_files(self.greek_path)

    def file_has_greek_averages(self, file_name):
        last_string_in_file_name = get_last_number_in_file_name(file_name)
        file_is_average = (last_string_in_file_name not in ["0", "Average"])
        return file_is_average

    def do_average_greek(self, file_name):
        file_path = os.path.join(self.greek_path, file_name)
        file_contents = get_file_contents(file_path)
        self.set_average_greek(file_contents)
        self.save_average_greek()

    def set_average_greek(self, file_contents):
        for greek_obj in self.greek_objects:
            greek_obj.set_greek_averages(file_contents)

    def save_average_greek(self):
        self.set_average_greek_file_path()
        with open(self.average_greek_file_path, "w+") as file:
            file.writelines(f"Detuning (Hz)\tDrift (Hz)\tOmega (Hz)\tStandard deviation (Hz)\tGamma (Hz)\tStandard deviation (Hz)\tAmplitude (mW)\tStandard deviation (mW)\n")
            for detuning_obj in self.greek_objects:
                file = self.write_average_greek_to_file(file, detuning_obj)

    def set_average_greek_file_path(self):
        greek_folder_path = self.trial.data_set.greek_path
        data_set = self.trial.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial_number = self.trial.trial_number
        file_name = f"{data_set}_Power_{power}_Trial_{trial_number}_Average.txt"
        self.average_greek_file_path = os.path.join(greek_folder_path, file_name)

    def write_average_greek_to_file(self, file, detuning_obj):
        if detuning_obj.omega_average is not None:
            file = self.do_write_average_greek_to_file(file, detuning_obj)
        return file

    def do_write_average_greek_to_file(self, file, detuning_obj):
        file = self.write_drift_average_to_file(file, detuning_obj)
        file = self.write_omega_average_to_file(file, detuning_obj)
        file = self.write_gamma_average_to_file(file, detuning_obj)
        file = self.write_amplitude_average_to_file(file, detuning_obj)
        return file

    def write_drift_average_to_file(self, file, detuning_obj):
        detuning = detuning_obj.detuning.detuning
        drift_average = detuning_obj.drift_average
        file.writelines(f"{detuning}\t{drift_average}\t")
        return file

    def write_omega_average_to_file(self, file, detuning_obj):
        omega_average = detuning_obj.omega_average
        omega_deviation = detuning_obj.omega_deviation
        file.writelines(f"{omega_average}\t{omega_deviation}\t")
        return file

    def write_gamma_average_to_file(self, file, detuning_obj):
        gamma_average = detuning_obj.gamma_average
        gamma_deviation = detuning_obj.gamma_deviation
        file.writelines(f"{gamma_average}\t{gamma_deviation}\t")
        return file

    def write_amplitude_average_to_file(self, file, detuning_obj):
        amplitude_average = detuning_obj.amplitude_average
        amplitude_deviation = detuning_obj.amplitude_deviation
        file.writelines(f"{amplitude_average}\t{amplitude_deviation}\n")
        return file
    
    def set_greek_children(self):
        self.path = self.trial.data_set.greek_path
        self.set_files()
        self.set_children()

    def set_trial_from_file(self):
        self.trial.set_transmission()
        self.trial.set_spectrum()

    def get_label_from_average_size(self, average_size):
        if average_size is None:
            label = "AllSpectraAveraged"
        else:
            label = str(average_size)
        return label
    
    def get_label_from_file_name(self, file_name):
        label = file_name[file_name.index("l") + 4:-4]
        if label == "":
            label = "NoLabel"
        return label
    
    def set_files(self):
        self.files = self.trial.get_data_files(self.path)

    def set_children(self):
        self.children = [self.get_child(file_name) for file_name in self.files]

    def get_child(self, file_name):
        child = self.get_base_child(file_name)
        return child

    def get_base_child(self, file_name):
        label = self.get_label_from_file_name(file_name)
        path = os.path.join(self.path, file_name)
        base_child = Greek(self.trial, self, label)
        base_child.extract_from_path(path)
        return base_child
