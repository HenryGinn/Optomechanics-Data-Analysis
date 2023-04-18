import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_group_indices
from Utils import get_file_contents_from_path

class AverageSpectra(Feature):

    name = "Average Spectra"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()

    def process_kwargs(self, **kwargs):
        self.kwargs = kwargs
        self.process_average_size_kwarg()

    def process_average_size_kwarg(self):
        if "average" in self.kwargs:
            self.average_size = self.kwargs["average"]
        else:
            self.average_size = None

    def set_paths(self):
        self.set_folder_path()
        for power_obj in self.data_set_obj.power_objects:
            self.set_power_path(power_obj)
            self.set_trial_paths(power_obj)

    def set_power_path(self, power_obj):
        path = os.path.join(self.folder_path, power_obj.power_string)
        power_obj.average_spectra_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.average_spectra_path,
                            f"Trial {trial_obj.trial_number}")
        trial_obj.average_spectra_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        self.set_label_name()
        base_path = self.get_base_detuning_path(detuning_obj)
        path = os.path.join(base_path, f"AverageSize_{self.label}")
        detuning_obj.average_spectra_path = path
        make_folder(path)

    def get_base_detuning_path(self, detuning_obj):
        base_path = os.path.join(detuning_obj.trial_obj.average_spectra_path,
                                 f"{detuning_obj.detuning} Hz")
        make_folder(base_path)
        return base_path

    def set_label_name(self):
        if self.average_size is None:
            self.label = "AllSpectraAveraged"
        else:
            self.label = str(self.average_size)

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_valid("Load")
        self.data_set_obj.spectra_peak("Load")

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
        indices = self.get_spectrum_indices(detuning_obj)
        if len(indices) != 0:
            self.set_average_spectra(detuning_obj, indices)
        else:
            detuning_obj.average_spectrum_objects = []

    def get_spectrum_indices(self, detuning_obj):
        spectrum_indices = [index
                            for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects)
                            if spectrum_obj.has_valid_peak]
        return spectrum_indices

    def set_average_spectra(self, detuning_obj, indices):
        group_indices_all = get_group_indices(len(indices), self.average_size)
        detuning_obj.average_spectrum_objects = [self.get_average_spectrum(detuning_obj, group_indices, indices, index)
                                                 for index, group_indices in enumerate(group_indices_all)]

    def get_average_spectrum(self, detuning_obj, group_indices, indices, index):
        spectrum_indices = np.array(indices)[group_indices]
        spectrum_objects = np.array(detuning_obj.spectrum_objects)[spectrum_indices]
        file_path = os.path.join(detuning_obj.average_spectra_path, f"Group_{index}.txt")
        average_spectrum_obj = Spectrum(detuning_obj, file_path)
        average_spectrum_obj.S21 = self.get_average_S21(average_spectrum_obj, spectrum_objects)
        return average_spectrum_obj

    def get_average_S21(self, average_spectrum_obj, spectrum_objects):
        self.offset_data(average_spectrum_obj, spectrum_objects)
        group_S21_offsets = [spectrum_obj.S21_offset for spectrum_obj in spectrum_objects]
        average_S21 = np.mean(group_S21_offsets, axis = 0)
        return average_S21

    def offset_data(self, average_spectrum_obj, spectrum_objects):
        self.set_peak_index_data(average_spectrum_obj, spectrum_objects)
        for spectrum_obj in spectrum_objects:
            self.set_S21_offset(average_spectrum_obj, spectrum_obj)
        self.set_frequency(average_spectrum_obj)

    def set_peak_index_data(self, average_spectrum_obj, spectrum_objects):
        average_spectrum_obj.peak_indexes = [spectrum_obj.peak_index for spectrum_obj in spectrum_objects]
        average_spectrum_obj.min_peak_index = min(average_spectrum_obj.peak_indexes)
        average_spectrum_obj.max_peak_index = max(average_spectrum_obj.peak_indexes)

    def set_S21_offset(self, average_spectrum_obj, spectrum_obj):
        spectrum_obj.load_S21()
        left_index = spectrum_obj.peak_index - average_spectrum_obj.min_peak_index
        right_index = len(spectrum_obj.S21) - (average_spectrum_obj.max_peak_index - spectrum_obj.peak_index)
        spectrum_obj.S21_offset = spectrum_obj.S21[left_index:right_index]

    def set_frequency(self, average_spectrum_obj):
        cutoff_size = average_spectrum_obj.max_peak_index - average_spectrum_obj.min_peak_index
        frequency_offset_length = len(average_spectrum_obj.frequency) - cutoff_size
        average_spectrum_obj.frequency = np.copy(average_spectrum_obj.frequency[:frequency_offset_length])
        average_spectrum_obj.frequency_shift = average_spectrum_obj.frequency[average_spectrum_obj.min_peak_index]
        average_spectrum_obj.frequency -= average_spectrum_obj.frequency_shift

    def save_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)
            self.save_detuning_obj(detuning_obj)

    def save_detuning_obj(self, detuning_obj):
        for average_spectrum_obj in detuning_obj.average_spectrum_objects:
            with open(average_spectrum_obj.file_path, "w") as file:
                self.save_average_spectrum_obj_to_file(average_spectrum_obj, file)

    def save_average_spectrum_obj_to_file(self, average_spectrum_obj, file):
        file.writelines("S21\tFrequency (Hz)\n")
        for S21, frequency in zip(average_spectrum_obj.S21, average_spectrum_obj.frequency):
            file.writelines(f"{S21}\t{frequency}\n")

    def data_is_saved(self):
        return np.all([(len(list(os.listdir(detuning_obj.average_spectra_path))) > 0)
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
