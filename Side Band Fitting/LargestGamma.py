import os

import numpy as np

from AverageDetuning import AverageDetuning
from Utils import get_file_contents
from Utils import get_last_number_in_file_name

class LargestGamma():

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj

    def find_largest_gamma(self):
        self.set_largest_gamma_dict()
        self.create_output_files()

    def set_largest_gamma_dict(self):
        self.largest_gamma_dict = {greek_trial: self.get_detunings_file_dicts(greek_trial)
                                   for power_obj in self.data_set_obj.power_objects
                                   for greek_trial in power_obj.greek_objects}

    def get_detunings_file_dicts(self, greek_trial):
        greek_trial.set_greek_files()
        greek_files_non_average = self.get_greek_files_non_average(greek_trial)
        detunings = self.get_detunings(greek_trial, greek_files_non_average)
        return detunings

    def get_greek_files_non_average(self, greek_trial):
        greek_files_non_average = [file_name for file_name in greek_trial.greek_files
                                   if not file_name.endswith("Average.txt")]
        return greek_files_non_average

    def get_detunings(self, greek_trial, greek_files_non_average):
        detunings = [self.get_detunings_file_dict(greek_trial, file_name)
                     for file_name in greek_files_non_average]
        return detunings

    def get_detunings_file_dict(self, greek_trial, file_name):
        self.extract_from_file(greek_trial, file_name)
        group_index, detuning_value = self.get_average_data_position()
        detuning_obj = self.get_detuning_obj(greek_trial, detuning_value)
        detuning_file_dict = self.construct_detuning_file_dict(detuning_obj, group_index, file_name)
        return detuning_file_dict

    def extract_from_file(self, greek_trial, file_name):
        greek_trial.set_trial_from_file()
        file_contents = self.get_file_contents(greek_trial, file_name)
        self.extract_file_contents(file_contents)

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

    def get_average_size_from_file_name(self, file_name):
        label = get_last_number_in_file_name(file_name)
        try:
            average_size = int(label)
        except:
            average_size = None
        return average_size

    def get_average_data_position(self):
        max_gamma_index = np.argmax(self.gamma)
        detuning_value = self.detuning[max_gamma_index]
        group_index = self.get_group_index(detuning_value)
        return group_index, detuning_value

    def get_group_index(self, detuning_value):
        gamma_filtered = [gamma for detuning, gamma in zip(self.detuning, self.gamma)
                          if detuning == detuning_value]
        group_index = gamma_filtered.index(np.max(self.gamma))
        return group_index

    def get_detuning_obj(self, greek_trial, detuning_value):
        detuning_objects = greek_trial.trial.detuning_objects
        detuning_obj = [detuning_obj for detuning_obj in detuning_objects
                        if detuning_obj.detuning == detuning_value][0]
        return detuning_obj

    def construct_detuning_file_dict(self, detuning_obj, group_index, file_name):
        S21_average_obj = self.get_S21_average_obj(detuning_obj, group_index, file_name)
        detuning_file_dict = {"File": file_name,
                              "Frequency": S21_average_obj.frequency,
                              "S21": S21_average_obj.S21}
        return detuning_file_dict

    def get_S21_average_obj(self, detuning_obj, group_index, file_name):
        average_size = self.get_average_size_from_file_name(file_name)
        average_detuning = AverageDetuning(detuning_obj)
        average_detuning.set_S21_average_objects(average_size)
        S21_average_obj = average_detuning.S21_average_objects[group_index]
        return S21_average_obj

    def create_output_files(self):
        for greek_trial, detuning_file_dicts in self.largest_gamma_dict.items():
            for detuning_file_dict in detuning_file_dicts:
                self.create_output_file(greek_trial, detuning_file_dict)

    def create_output_file(self, greek_trial, detuning_file_dict):
        output_path = self.get_output_path(greek_trial, detuning_file_dict)
        with open(output_path, "w") as file:
            file.writelines("Realigned Frequency (Hz)\tS21 (mW)\n")
            self.output_results_to_file(detuning_file_dict, file)

    def get_output_path(self, greek_trial, detuning_file_dict):
        data_file_name = detuning_file_dict["File"]
        file_name = self.get_file_name(greek_trial, data_file_name)
        output_path = os.path.join(self.data_set_obj.max_gamma_S21_path, file_name)
        return output_path

    def get_file_name(self, greek_trial, data_file_name):
        power = greek_trial.trial.power_obj.power_string
        trial_number = greek_trial.trial.trial_number
        label = get_last_number_in_file_name(data_file_name)
        file_name = f"Power_{power}_Trial_number_{trial_number}_Label_{label}.txt"
        return file_name

    def output_results_to_file(self, detuning_file_dict, file):
        frequencies = detuning_file_dict["Frequency"]
        S21s = detuning_file_dict["S21"]
        for frequency, S21 in zip(frequencies, S21s):
            file.writelines(f"{frequency}\t{S21}\n")
