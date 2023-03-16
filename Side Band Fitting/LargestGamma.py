import os

import numpy as np

from Utils import get_file_contents
from Utils import get_last_number_in_file_name

class LargestGamma():

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj

    def find_largest_gamma(self):
        self.set_largest_gamma_dict()
        output_path = self.get_output_path()
        self.create_output_file(output_path)

    def set_largest_gamma_dict(self):
        self.largest_gamma_dict = {(power, greek_trial): self.get_detunings_file_dicts(greek_trial)
                                   for power in self.data_set_obj.power_objects
                                   for greek_trial in power.greek_objects}

    def get_detunings_file_dicts(self, greek_trial):
        greek_trial.set_greek_files()
        detunings = [self.get_detunings_file_dict(greek_trial, file_name)
                     for file_name in greek_trial.greek_files]
        return detunings

    def get_detunings_file_dict(self, greek_trial, file_name):
        file_contents = self.get_file_contents(greek_trial, file_name)
        self.extract_file_contents(file_contents)
        max_gamma_index = np.argmax(self.gamma)
        print(greek_trial.trial.
        detuning_of_largest_gamma = self.detuning[max_gamma_index] - self.drift[max_gamma_index]
        detuning_file_dict = {"Detuning": detuning_of_largest_gamma, "File": file_name}
        return detuning_file_dict

    def get_file_contents(self, greek_trial, file_name):
        file_path = os.path.join(greek_trial.greek_path, file_name)
        file_contents = get_file_contents(file_path)
        file_contents = [np.array(column) for column in zip(*file_contents)]
        return file_contents

    def extract_file_contents(self, file_contents):
        if len(file_contents) == 5:
            self.detuning, self.drift, _, self.gamma, _ = file_contents
        else:
            self.detuning, self.drift, _, _, self.gamma, *_ = file_contents

    def get_output_path(self):
        output_file_name = f"Detuning of Largest Gamma for {self.data_set_obj.folder_name}"
        output_path = os.path.join(self.data_set_obj.data_set_results_path, output_file_name)
        return output_path

    def create_output_file(self, output_path):
        with open(output_path, "w") as file:
            file.writelines("Power (dBm)\tTrial Number\tDetuning of Largest Gamma\tFile Label\n")
            self.output_results_to_file(file)

    def output_results_to_file(self, file):
        for (power_obj, greek_trial), detuning_file_dicts in self.largest_gamma_dict.items():
            power = power_obj.power_string
            trial_number = greek_trial.trial.trial_number
            for detuning_file_dict in detuning_file_dicts:
                detuning = detuning_file_dict["Detuning"]
                file_label = get_last_number_in_file_name(detuning_file_dict["File"])
                file.writelines(f"{power}\t{trial_number}\t{detuning}\t{file_label}\n")
