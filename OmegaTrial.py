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
        self.trial.set_S21()
        self.trial.process_transmission()

    def write_omega_to_file(self, file):
        for omega_obj in self.omega_objects:
            if omega_obj.detuning.valid:
                omegas, drifts = omega_obj.get_omegas_all()
                file = self.save_detuning_omega(file, omegas, drifts, omega_obj.detuning.detuning)
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
        for omega, drift, deviation in zip(self.omegas, self.drifts, self.deviations):
            file.writelines(f"{detuning}\t{drift}\t{omega}\t{deviation}\n")
        return file

    def get_omega_file_path(self, label):
        data_set = self.trial.power_obj.data_set.folder_name
        omega_file_name = self.get_omega_file_name(data_set, label)
        parent_path = self.trial.power_obj.data_set.omega_path
        omega_file_path = os.path.join(parent_path, omega_file_name)
        return omega_file_path

    def get_omega_file_name(self, data_set, label):
        if label is None:
            omega_file_name = f"{data_set}_{self.trial.power_obj.folder_name}_{self.trial.trial_number}.txt"
        else:
            omega_file_name = f"{data_set}_{self.trial.power_obj.folder_name}_{self.trial.trial_number}_{label}.txt"
        return omega_file_name
