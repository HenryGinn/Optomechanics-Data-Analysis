import os
from GammaDetuning import GammaDetuning

class GammaTrial():

    def __init__(self, trial_obj):
        self.trial = trial_obj
        self.create_gamma_objects()

    def create_gamma_objects(self):
        self.gamma_objects = [GammaDetuning(detuning_obj)
                              for detuning_obj in self.trial.detuning_objects]

    def process_gamma(self, average_size):
        self.trial.set_spectrum()
        self.trial.set_transmission()
        for gamma_obj in self.gamma_objects:
            if gamma_obj.detuning.valid:
                print(f"Detuning: {gamma_obj.detuning.detuning}")
                gamma_obj.set_gamma_averages(average_size)

    def get_gamma_file_path(self, average_size):
        gamma_file_name = self.get_gamma_file_name(average_size)
        parent_path = self.trial.power_obj.data_set.gamma_path
        gamma_file_path = os.path.join(parent_path, gamma_file_name)
        return gamma_file_path

    def get_gamma_file_name(self, average_size):
        gamma_file_name = self.get_gamma_base_file_name()
        if average_size is not None:
            gamma_file_name = f"{gamma_file_name}_{average_size}"
        gamma_file_name = f"{gamma_file_name}.txt"
        return gamma_file_name

    def get_gamma_base_file_name(self):
        data_set = self.trial.power_obj.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial = self.trial.trial_number
        base_file_name = f"{data_set}_Power_{power}_Trial_{trial}"
        return base_file_name

    def save_gamma(self, average_size):
        gamma_file_path = self.get_gamma_file_path(average_size)
        with open(gamma_file_path, "w") as file:
            file.writelines(f"Detuning\tDrift\tGamma\n")
            for gamma_obj in self.gamma_objects:
                if gamma_obj.detuning.valid:
                    file = gamma_obj.save_gamma(file)

    def set_gamma_files(self):
        if hasattr(self, "gamma_files") is False:
            self.gamma_path = self.trial.data_set.gamma_path
            self.gamma_files = self.trial.get_data_files(self.gamma_path)

    def average_gamma(self):
        self.set_gamma_files()
        for file_name in self.gamma_files:
            if self.file_has_gamma_averages(file_name):
                self.do_average_gamma(file_name)

    def file_has_gamma_averages(self, file_name):
        last_number_in_file_name = self.get_last_number_in_file_name(file_name)
        file_is_average = (last_number_in_file_name != "0")
        return file_is_average

    def get_last_number_in_file_name(self, file_name):
        underscore_locations = self.trial.get_underscore_locations(file_name)
        left = underscore_locations[-1] + 1
        right = len(file_name) - 4
        last_number_in_file_name = file_name, file_name[left:right]
        return last_number_in_file_name

    def do_average_gamma(self, file_name):
        file_path = os.path.join(self.gamma_path, file_name)
        file_contents = self.trial.get_file_contents(file_path)
        self.set_average_gamma(file_contents)
        self.save_average_gamma()

    def set_average_gamma(self, file_contents):
        for gamma_obj in self.gamma_objects:
            gamma_obj.set_average_gamma(file_contents)

    def save_average_gamma(self):
        self.set_average_gamma_file_path()
        with open(self.average_gamma_file_path, "w+") as file:
            file.writelines(f"Detuning (Hz)\tDrift(Hz)\tGamma (Hz)\t\n")
            for detuning_obj in self.gamma_objects:
                file = self.write_average_gamma_to_file(file, detuning_obj)

    def set_average_gamma_file_path(self):
        gamma_folder_path = self.trial.data_set.gamma_path
        data_set = self.trial.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial_number = self.trial.trial_number
        file_name = f"{data_set}_Power_{power}_Trial_{trial_number}_Average.txt"
        self.average_gamma_file_path = os.path.join(gamma_folder_path, file_name)

    def write_average_gamma_to_file(self, file, detuning_obj):
        drift = detuning_obj.average_drift
        gamma = detuning_obj.average_gamma
        detuning = detuning_obj.detuning.detuning
        file.writelines(f"{detuning}\t{drift}\t{gamma}\n")
        return file
