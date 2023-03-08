from copy import deepcopy
import os
from GreekTrial import GreekTrial
from OmegaDetuning import OmegaDetuning
from Greek import Greek

class OmegaTrial(GreekTrial):

    def __init__(self, trial_obj):
        GreekTrial.__init__(self, trial_obj)
        self.name = "Omega"
        self.name_latex = r"$\Omega_m$"
        self.offset_by_0_value = True
        self.create_omega_objects()

    def create_omega_objects(self):
        self.omega_objects = [OmegaDetuning(detuning_obj)
                              for detuning_obj in self.trial.detuning_objects]

    def process_omega_all(self):
        self.initialise_omega_all()
        self.set_trial_from_file()
        self.create_omega_all_file()

    def initialise_omega_all(self):
        self.trial.omega_all = Greek(self.trial, self, "All")
        self.trial.omega_all.path = self.get_omega_file_path("All")

    def create_omega_all_file(self):
        with open(self.trial.omega_all.path, "w") as file:
            file.writelines(f"Detuning\tDrift\tOmega\n")
            file = self.write_omega_to_file(file)

    def write_omega_to_file(self, file):
        for omega_obj in self.omega_objects:
            if omega_obj.detuning.valid:
                omega_obj.set_omegas_all()
                file = self.save_detuning_omega(file, omega_obj)
        return file

    def omega_average(self, average_size):
        self.read_from_omega_all()
        self.initialise_omega_average(average_size)
        self.create_omega_average_file(average_size)

    def read_from_omega_all(self):
        self.initialise_omega_all()
        path = self.trial.omega_all.path
        self.try_read_from_omega_all(path)

    def try_read_from_omega_all(self, path):
        try:
            self.trial.omega_all.extract_from_path(path)
        except:
            raise Exception("Cannot find omega all file.\nRun process_omega method")

    def initialise_omega_average(self, average_size):
        label = self.get_label_from_average_size(average_size)
        self.omega_average = Greek(self.trial, self, label)
        self.omega_average.path = self.get_omega_file_path(label)

    def create_omega_average_file(self, average_size):
        with open(self.omega_average.path, "w") as file:
            file.writelines(f"Detuning\tDrift\tOmega\tStandard Deviation\n")
            for omega_obj in self.omega_objects:
                omega_obj.set_omegas_averages(average_size)
                self.save_detuning_omega(file, omega_obj)

    def save_detuning_omega(self, file, omega_obj):
        if omega_obj.omegas is not None:
            file = self.do_save_detuning_omega(file, omega_obj)
        return file

    def do_save_detuning_omega(self, file, omega_obj):
        if hasattr(omega_obj, "deviations"):
            self.save_detuning_omega_deviation(file, omega_obj)
        else:
            self.save_detuning_omega_no_deviation(file, omega_obj)
        return file

    def save_detuning_omega_deviation(self, file, omega_obj):
        detuning = omega_obj.detuning.detuning
        for omega, drift, deviation in zip(omega_obj.omegas,
                                           omega_obj.drifts,
                                           omega_obj.deviations):
            file.writelines(f"{detuning}\t{drift}\t{omega}\t{deviation}\n")

    def save_detuning_omega_no_deviation(self, file, omega_obj):
        detuning = omega_obj.detuning.detuning
        for omega, drift in zip(omega_obj.omegas, omega_obj.drifts):
            file.writelines(f"{detuning}\t{drift}\t{omega}\n")
        return file

    def get_omega_file_path(self, label):
        omega_file_name = self.get_omega_file_name(label)
        omega_folder_path = self.trial.data_set.omega_path
        omega_file_path = os.path.join(omega_folder_path, omega_file_name)
        return omega_file_path

    def get_omega_file_name(self, label):
        data_set = self.trial.power_obj.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial = self.trial.trial_number
        omega_file_name = f"{data_set}_Power_{power}_Trial_{trial}_{label}.txt"
        return omega_file_name

    def set_omega_children(self):
        self.path = self.trial.data_set.omega_path
        self.set_files()
        self.set_children()
