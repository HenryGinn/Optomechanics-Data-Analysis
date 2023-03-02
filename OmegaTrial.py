from copy import deepcopy
import os
from OmegaDetuning import OmegaDetuning

class OmegaTrial():

    def __init__(self, trial_obj):
        self.trial = trial_obj
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

    def output_omegas(self, omegas, drifts, detuning):
        print(f"\nMain detuning: {detuning}")
        for omega, drift in zip(omegas, drifts):
            print(f"Drift: {drift}, Omega: {omega}")
        print("")

    def omega_average(self, average_size):
        self.set_omega_all_file_path()
        omega_file_path = self.get_omega_file_path(average_size)
        with open(omega_file_path, "w") as file:
            file.writelines(f"Detuning\tDrift\tOmega\tStandard Deviation\n")
            for omega_obj in self.omega_objects:
                self.omegas, self.drifts, self.deviations = omega_obj.get_omegas_averages(average_size)
                file = self.save_detuning_omega(file, omega_obj.detuning.detuning)

    def save_detuning_omega(self, file, detuning):
        if hasattr(self, "deviations"):
            self.save_detuning_omega_deviation(file, detuning)
        else:
            self.save_detuning_omega_no_deviation(file, detuning)
        return file

    def save_detuning_omega_deviation(self, file, detuning):
        if self.omegas is not None:
            for omega, drift, deviation in zip(self.omegas, self.drifts, self.deviations):
                file.writelines(f"{detuning}\t{drift}\t{omega}\t{deviation}\n")
        return file

    def save_detuning_omega_no_deviation(self, file, detuning):
        for omega, drift in zip(self.omegas, self.drifts):
            file.writelines(f"{detuning}\t{drift}\t{omega}\n")
        return file

    def get_omega_file_path(self, label):
        omega_file_name = self.get_omega_file_name(label)
        parent_path = self.trial.power_obj.data_set.omega_path
        omega_file_path = os.path.join(parent_path, omega_file_name)
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
        if hasattr(self, "omega_files") is False:
            self.omega_path = self.trial.data_set.omega_path
            self.omega_files = self.trial.get_data_files(self.omega_path)
