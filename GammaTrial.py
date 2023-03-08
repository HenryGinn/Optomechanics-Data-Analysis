import os
from GammaDetuning import GammaDetuning
from GreekTrial import GreekTrial
from Greek import Greek
from Utils import get_file_contents
from Utils import get_last_number_in_file_name

class GammaTrial(GreekTrial):

    def __init__(self, trial_obj):
        GreekTrial.__init__(self, trial_obj)
        self.name = "Gamma"
        self.name_latex = r"$\Gamma_m$"
        self.offset_by_0_value = False
        self.create_gamma_objects()

    def create_gamma_objects(self):
        self.gamma_objects = [GammaDetuning(detuning_obj)
                              for detuning_obj in self.trial.detuning_objects]

    def process_gamma(self, average_size):
        self.set_trial_from_file()
        self.create_gamma_average_obj(average_size)
        self.create_gamma_average_file(average_size)

    def create_gamma_average_obj(self, average_size):
        label = self.get_label_from_average_size(average_size)
        self.trial.gamma_average = Greek(self.trial, self, label)
        self.trial.gamma_average.path = self.get_gamma_file_path(average_size)

    def create_gamma_average_file(self, average_size):
        with open(self.trial.gamma_average.path, "w") as file:
            file.writelines(f"Detuning\tDrift\tGamma\n")
            file = self.write_gamma_to_file(file, average_size)

    def write_gamma_to_file(self, file, average_size):
        for gamma_obj in self.gamma_objects:
            if gamma_obj.detuning.valid:
                gamma_obj.set_gamma_averages(average_size)
                file = gamma_obj.save_gamma(file)
        return file

    def get_gamma_file_path(self, average_size):
        gamma_file_name = self.get_gamma_file_name(self.trial.gamma_average.label)
        parent_path = self.trial.power_obj.data_set.gamma_path
        gamma_file_path = os.path.join(parent_path, gamma_file_name)
        return gamma_file_path

    def get_gamma_file_name(self, label):
        data_set = self.trial.power_obj.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial = self.trial.trial_number
        file_name = f"{data_set}_Power_{power}_Trial_{trial}_{label}.txt"
        return file_name

    def average_gamma(self):
        self.set_gamma_files()
        for file_name in self.gamma_files:
            if self.file_has_gamma_averages(file_name):
                self.do_average_gamma(file_name)

    def set_gamma_files(self):
        if hasattr(self, "gamma_files") is False:
            self.gamma_path = self.trial.data_set.gamma_path
            self.gamma_files = self.trial.get_data_files(self.gamma_path)

    def file_has_gamma_averages(self, file_name):
        last_string_in_file_name = get_last_number_in_file_name(file_name)
        file_is_average = (last_string_in_file_name not in ["0", "Average"])
        return file_is_average

    def do_average_gamma(self, file_name):
        file_path = os.path.join(self.gamma_path, file_name)
        file_contents = get_file_contents(file_path)
        self.set_average_gamma(file_contents)
        self.save_average_gamma()

    def set_average_gamma(self, file_contents):
        for gamma_obj in self.gamma_objects:
            gamma_obj.set_average_gamma(file_contents)

    def save_average_gamma(self):
        self.set_average_gamma_file_path()
        with open(self.average_gamma_file_path, "w+") as file:
            file.writelines(f"Detuning (Hz)\tDrift (Hz)\tGamma (Hz)\tStandard deviation (Hz)\n")
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
        if detuning_obj.average_gamma is not None:
            file = self.do_write_average_gamma_to_file(file, detuning_obj)
        return file

    def do_write_average_gamma_to_file(self, file, detuning_obj):
        detuning = detuning_obj.detuning.detuning
        drift = detuning_obj.average_drift
        gamma = detuning_obj.average_gamma
        deviation = detuning_obj.deviation
        file.writelines(f"{detuning}\t{drift}\t{gamma}\t{deviation}\n")
        return file
    
    def set_gamma_children(self):
        self.path = self.trial.data_set.gamma_path
        self.set_files()
        self.set_children()
