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
        gamma_file_path = self.get_gamma_file_path(average_size)
        self.trial.set_S21()
        for gamma_obj in self.gamma_objects:
            print(f"Detuning: {gamma_obj.detuning.detuning}")
            gamma_obj.set_gamma_averages(average_size)

    def get_gamma_file_path(self, average_size):
        data_set = self.trial.power_obj.data_set.folder_name
        gamma_file_name = self.get_gamma_file_name(data_set, average_size)
        parent_path = self.trial.power_obj.data_set.gamma_path
        gamma_file_path = os.path.join(parent_path, gamma_file_name)
        return gamma_file_path

    def get_gamma_file_name(self, data_set, average_size):
        if average_size is None:
            gamma_file_name = f"{data_set}_{self.trial.power_obj.folder_name}_{self.trial.trial_number}.txt"
        else:
            gamma_file_name = f"{data_set}_{self.trial.power_obj.folder_name}_{self.trial.trial_number}_{average_size}.txt"
        return gamma_file_name

    def save_gamma(self, average_size):
        gamma_file_path = self.get_gamma_file_path(average_size)
        with open(gamma_file_path, "w") as file:
            file.writelines(f"Detuning\tDrift\tGamma\n")
            for gamma_obj in self.gamma_objects:
                file = gamma_obj.save_gamma(file)
