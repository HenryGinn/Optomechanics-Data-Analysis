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
        base_file_name = self.get_gamma_base_file_name()
        if average_size is not None:
            gamma_file_name = f"{base_file_name}_{average_size}"
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
