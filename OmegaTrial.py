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
        self.setup_omega_all()
        with open(self.trial.omega_all_file_path, "w") as file:
            file.writelines(f"Detuning\tDrift\tOmega\n")
            file = self.write_omega_to_file(file)

    def setup_omega_all(self):
        self.set_omega_all_file_path()
        self.trial.set_spectrum()
        self.trial.set_transmission()

    def write_omega_to_file(self, file):
        for omega_obj in self.omega_objects:
            if omega_obj.detuning.valid:
                self.omegas, self.drifts = omega_obj.get_omegas_all()
                file = self.save_detuning_omega(file, omega_obj.detuning.detuning)
        return file

    def set_omega_all_file_path(self):
        self.trial.omega_all_file_path = self.get_omega_file_path("All")

    def omega_average(self, average_size):
        self.set_omega_all_file_path()
        omega_file_path = self.get_omega_file_path(average_size)
        with open(omega_file_path, "w") as file:
            file.writelines(f"Detuning\tDrift\tOmega\tStandard Deviation\n")
            for omega_obj in self.omega_objects:
                self.omegas, self.drifts, self.deviations = omega_obj.get_omegas_averages(average_size)
                self.save_detuning_omega(file, omega_obj.detuning.detuning)

    def save_detuning_omega(self, file, detuning):
        if self.omegas is not None:
            self.do_save_detuning_omega(file, detuning)
        return file

    def do_save_detuning_omega(self, file, detuning):
        if hasattr(self, "deviations"):
            self.save_detuning_omega_deviation(file, detuning)
        else:
            self.save_detuning_omega_no_deviation(file, detuning)
        return file

    def save_detuning_omega_deviation(self, file, detuning):
        if self.omegas is not None:
            for omega, drift, deviation in zip(self.omegas, self.drifts, self.deviations):
                file.writelines(f"{detuning}\t{drift}\t{omega}\t{deviation}\n")

    def save_detuning_omega_no_deviation(self, file, detuning):
        for omega, drift in zip(self.omegas, self.drifts):
            file.writelines(f"{detuning}\t{drift}\t{omega}\n")
        return file

    def get_omega_file_path(self, label):
        omega_file_name = self.get_omega_file_name(label)
        omega_file_path = os.path.join(self.path, omega_file_name)
        return omega_file_path

    def get_omega_file_name(self, label):
        omega_file_name = self.get_base_omega_file_name()
        if label is not None:
            omega_file_name = f"{omega_file_name}_{label}"
        omega_file_name = f"{omega_file_name}.txt"
        return omega_file_name

    def get_base_omega_file_name(self):
        data_set = self.trial.power_obj.data_set.folder_name
        power = self.trial.power_obj.folder_name
        trial = self.trial.trial_number
        base_omega_file_name = f"{data_set}_Power_{power}_Trial_{trial}"
        return base_omega_file_name

    def set_omega_files(self):
        self.path = self.trial.data_set.omega_path
        self.omega_files = self.trial.get_data_files(self.path)

    def set_omega_children(self):
        self.omega_children = [self.get_omega_child(file_name)
                               for file_name in self.omega_files]

    def get_omega_child(self, file_name):
        label = self.get_label(file_name)
        omega_child = Greek(self.trial, self, label)
        omega_child.extract_from_file(file_name)
        return omega_child
