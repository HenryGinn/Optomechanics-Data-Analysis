import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class SpectraRaw(Feature):

    name = "Spectra Raw"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        pass

    def data_is_saved(self):
        return True

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        for spectrum_obj in detuning_obj.spectrum_objects:
            self.load_spectrum_obj(spectrum_obj)

    def load_spectrum_obj(self, spectrum_obj):
        file_contents = get_file_contents_from_path(spectrum_obj.file_path)
        voltage, spectrum_obj.frequency = file_contents
        self.set_S21(spectrum_obj, voltage)

    def set_S21(self, spectrum_obj, voltage):
        cable_attenuation = 2 * 2.3
        voltage = (10**((voltage - cable_attenuation)/10))/1000
        spectrum_obj.S21 = voltage / spectrum_obj.power