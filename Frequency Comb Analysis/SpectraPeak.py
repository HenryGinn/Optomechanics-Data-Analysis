import os

import numpy as np

from CombFunction import CombFunction
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class SpectraPeak(CombFunction):

    name = "Spectra Peak"

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
        drift_obj.spectra_peak_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)
            self.set_group_paths(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.drift_obj.spectra_peak_path,
                            f"{detuning_obj.detuning} Hz")
        detuning_obj.spectra_peak_path = path
        make_folder(path)

    def set_group_paths(self, detuning_obj):
        for group_obj in detuning_obj.group_objects:
            path = os.path.join(detuning_obj.spectra_peak_path,
                                f"Group {group_obj.group_number}.txt")
            group_obj.spectrum_peak_path = path


    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.save_data_detuning(detuning_obj)

    def save_data_detuning(self, detuning_obj):
        for group_obj in detuning_obj.group_objects:
            self.set_spectra_peak_group(group_obj)
            self.save_spectra_peak_group(group_obj)

    def set_spectra_peak_group(self, group_obj):
        for spectrum_obj in group_obj.spectrum_objects:
            spectrum_obj.set_S21_and_frequency_from_file()
            spectrum_obj.set_peak()

    def save_spectra_peak_group(self, group_obj):
        with open(group_obj.spectrum_peak_path, "w") as file:
            file.writelines("Spectrum Index\tPeak Index\tFrequency (Hz)\tAmplitude\n")
            self.save_spectrum_peak(group_obj, file)

    def save_spectrum_peak(self, group_obj, file):
        for index, spectrum_obj in enumerate(group_obj.spectrum_objects):
            peak_index = spectrum_obj.peak_index
            frequency = spectrum_obj.peak_frequency
            amplitude = spectrum_obj.peak_amplitude
            file.writelines(f"{index}\t{peak_index}\t{frequency}\t{amplitude}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(group_obj.spectrum_peak_path)
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
        file_contents = zip(*get_file_contents_from_path(group_obj.spectrum_peak_path))
        for spectrum_index, peak_index, frequency, amplitude in file_contents:
            spectrum_obj = group_obj.spectrum_objects[int(spectrum_index)]
            spectrum_obj.peak_index = int(peak_index)
            spectrum_obj.peak_frequency = frequency
            spectrum_obj.peak_amplitude = amplitude
