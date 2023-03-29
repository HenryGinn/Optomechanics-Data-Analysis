import os

import numpy as np

from CombFunction import CombFunction
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class AlignSpectra(CombFunction):

    name = "Aligned Spectra"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, drift_obj.folder_name)
        drift_obj.aligned_spectra_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)
            self.set_group_paths(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.drift_obj.aligned_spectra_path,
                            f"{detuning_obj.detuning} Hz")
        detuning_obj.aligned_spectra_path = path
        make_folder(path)

    def set_group_paths(self, detuning_obj):
        for group_obj in detuning_obj.group_objects:
            path = os.path.join(detuning_obj.aligned_spectra_path,
                                f"Group {group_obj.group_number}.txt")
            group_obj.aligned_spectrum_path = path


    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.save_data_detuning(detuning_obj)

    def save_data_detuning(self, detuning_obj):
        for group_obj in detuning_obj.group_objects:
            self.set_aligned_spectra_group(group_obj)
            self.save_aligned_spectra_group(group_obj)

    def set_aligned_spectra_group(self, group_obj):
        self.process_spectrum_objects(group_obj)
        group_obj.spectrum_obj = Spectrum(group_obj)
        group_obj.spectrum_obj.frequency = group_obj.spectrum_objects[0].frequency
        self.align_spectra(group_obj)

    def process_spectrum_objects(self, group_obj):
        for spectrum_obj in group_obj.spectrum_objects:
            spectrum_obj.set_S21_and_frequency_from_file()
            spectrum_obj.set_peak()

    def align_spectra(self, group_obj):
        self.set_peak_indexes(group_obj)
        self.set_max_and_min_peak_indexes(group_obj)
        self.offset_S21(group_obj)
        self.offset_frequency(group_obj)
        group_obj.spectrum_obj.S21 = np.mean([spectrum_obj.S21_offset for spectrum_obj in group_obj.spectrum_objects], axis=0)

    def set_peak_indexes(self, group_obj):
        group_obj.peak_indexes = [spectrum_obj.peak_index
                             for spectrum_obj in group_obj.spectrum_objects]

    def set_max_and_min_peak_indexes(self, group_obj):
        group_obj.max_peak_index = max(group_obj.peak_indexes)
        group_obj.min_peak_index = min(group_obj.peak_indexes)

    def offset_S21(self, group_obj):
        for spectrum_obj in group_obj.spectrum_objects:
            self.set_S21_offset(spectrum_obj, group_obj)

    def set_S21_offset(self, spectrum_obj, group_obj):
        left_index = spectrum_obj.peak_index - group_obj.min_peak_index
        right_index = len(spectrum_obj.S21) - (group_obj.max_peak_index - spectrum_obj.peak_index)
        spectrum_obj.S21_offset = spectrum_obj.S21[left_index:right_index]

    def offset_frequency(self,group_obj):
        cutoff_size = group_obj.max_peak_index - group_obj.min_peak_index
        frequency_offset_length = len(group_obj.spectrum_obj.frequency) - cutoff_size
        group_obj.spectrum_obj.frequency = group_obj.spectrum_obj.frequency[:frequency_offset_length]
        frequency_shift = group_obj.spectrum_obj.frequency[group_obj.min_peak_index]
        group_obj.spectrum_obj.frequency -= frequency_shift

    def save_aligned_spectra_group(self, group_obj):
        with open(group_obj.aligned_spectrum_path, "w") as file:
            file.writelines("S21 (mW)\tFrequency (Hz)\n")
            self.save_aligned_spectrum(group_obj, file)

    def save_aligned_spectrum(self, group_obj, file):
        for S21, frequency in zip(group_obj.spectrum_obj.S21,
                                  group_obj.spectrum_obj.frequency):
            file.writelines(f"{S21}\t{frequency}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(group_obj.aligned_spectrum_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects
                       for group_obj in detuning_obj.group_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        for group_obj in detuning_obj.group_objects:
            self.load_group_obj(group_obj)

    def load_group_obj(self, group_obj):
        self.create_blank_spectrum_obj(group_obj)
        file_contents = get_file_contents_from_path(group_obj.aligned_spectrum_path)
        group_obj.spectrum_obj.S21, group_obj.spectrum_obj.frequency = file_contents

    def create_blank_spectrum_obj(self, group_obj):
        if not hasattr(group_obj, "spectrum_obj"):
            group_obj.spectrum_obj = Spectrum(self)

