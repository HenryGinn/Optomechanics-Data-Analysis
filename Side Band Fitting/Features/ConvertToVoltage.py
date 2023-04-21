import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_group_indices
from Utils import get_file_contents_from_path

class ConvertToVoltage(Feature):

    name = "Voltage Spectra"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()

    def process_kwargs(self, **kwargs):
        self.kwargs = kwargs
        self.process_voltage_size_kwarg()

    def process_voltage_size_kwarg(self):
        if "voltage" in self.kwargs:
            self.voltage_size = self.kwargs["voltage"]
        else:
            self.voltage_size = None

    def set_paths(self):
        self.set_folder_path()
        for power_obj in self.data_set_obj.power_objects:
            self.set_power_path(power_obj)
            self.set_trial_paths(power_obj)

    def set_power_path(self, power_obj):
        path = os.path.join(self.folder_path, power_obj.power_string)
        power_obj.voltage_spectra_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.voltage_spectra_path,
                            f"Trial {trial_obj.trial_number}")
        trial_obj.voltage_spectra_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        self.set_label_name()
        base_path = self.get_base_detuning_path(detuning_obj)
        path = os.path.join(base_path, f"AverageSize_{self.label}")
        detuning_obj.voltage_spectra_path = path
        make_folder(path)

    def get_base_detuning_path(self, detuning_obj):
        base_path = os.path.join(detuning_obj.trial_obj.voltage_spectra_path,
                                 f"{detuning_obj.detuning} Hz")
        make_folder(base_path)
        return base_path

    def set_label_name(self):
        if self.voltage_size is None:
            self.label = "AllSpectraAveraged"
        else:
            self.label = str(self.voltage_size)

    def load_necessary_data_for_saving(self):
        self.data_set_obj.average_spectra("Load")

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.save_power_obj(power_obj)

    def save_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_obj(trial_obj)
            self.save_trial_obj(trial_obj)

    def set_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)

    def set_detuning_obj(self, detuning_obj):
        detuning_obj.voltage_spectrum_objects = [self.get_voltage_spectrum(detuning_obj, average_spectrum_obj)
                                                 for average_spectrum_obj in detuning_obj.average_spectrum_objects]

    def get_voltage_spectrum(self, detuning_obj, average_spectrum_obj):
        file_path = self.get_file_path(average_spectrum_obj.file_path)
        voltage_spectrum_obj = Spectrum(detuning_obj, file_path)
        voltage_spectrum_obj.S21 = average_spectrum_obj.S21 * average_spectrum_obj.power
        voltage_spectrum_obj.frequency = average_spectrum_obj.frequency
        return voltage_spectrum_obj

    def get_file_path(self, old_file_path):
        file_path = old_file_path.replace("Average ", "Voltage ")
        return file_path

    def save_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)
            self.save_detuning_obj(detuning_obj)

    def save_detuning_obj(self, detuning_obj):
        for voltage_spectrum_obj in detuning_obj.voltage_spectrum_objects:
            with open(voltage_spectrum_obj.file_path, "w") as file:
                self.save_voltage_spectrum_obj_to_file(voltage_spectrum_obj, file)

    def save_voltage_spectrum_obj_to_file(self, voltage_spectrum_obj, file):
        file.writelines("Voltage (mW)\tFrequency (Hz)\n")
        for S21, frequency in zip(voltage_spectrum_obj.S21, voltage_spectrum_obj.frequency):
            file.writelines(f"{S21}\t{frequency}\n")

    def data_is_saved(self):
        return np.all([(len(list(os.listdir(detuning_obj.voltage_spectra_path))) > 0)
                       for power_obj in self.data_set_obj.power_objects
                       for trial_obj in power_obj.trial_objects
                       for detuning_obj in trial_obj.detuning_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        pass
