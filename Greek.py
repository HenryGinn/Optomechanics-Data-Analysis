import numpy as np
import os
from Utils import get_file_contents

class Greek():

    """
    An instance of this class is a single trend of greek data.
    Each greek file corresponds to one instance, and it is
    managed by OmegaTrial, GammaTrial, and GreekFigure
    """

    def __init__(self, trial_obj, greek_obj, label):
        self.trial_obj = trial_obj
        self.greek_obj = greek_obj
        self.label = label

    def extract_from_path(self, path):
        self.path = path
        file_contents = get_file_contents(path)
        self.set_detuning_and_greek(file_contents)

    def set_file_attributes(self, file_name):
        self.file_name = file_name
        self.file_path = os.path.join(self.greek_obj.path, self.file_name)
        
    def set_detuning_and_greek(self, file_contents):
        if len(file_contents) != 0:
            self.set_detuning_and_greek_from_file(file_contents)
        else:
            print("Warning: no data could be extracted from file in Greek")
            self.detuning, self.drift, self.greek = None, None, None

    def set_detuning_and_greek_from_file(self, file_contents):
        if len(file_contents[0]) == 3:
            self.detuning, self.drift, self.greek = zip(*file_contents)
            self.deviations = None
        else:
            self.detuning, self.drift, self.greek, self.deviations = zip(*file_contents)
        self.process_file_output()
        self.x_values = self.detuning - self.drift

    def process_file_output(self):
        self.process_greek()
        acceptable_indices = self.get_acceptable_indices(self.greek)
        self.detuning = np.array(self.detuning)[acceptable_indices]
        self.drift = np.array(self.drift)[acceptable_indices]
        self.greek = np.array(self.greek)[acceptable_indices]
        self.filter_deviations(acceptable_indices)

    def process_greek(self):
        self.greek = np.abs(self.greek)
        if self.greek_obj.offset_by_0_value:
            self.offset_greek_by_0_value()

    def offset_greek_by_0_value(self):
        detuning_0_index = self.get_detuning_0_index()
        self.greek_0_value = self.greek[detuning_0_index]
        self.greek -= self.greek_0_value

    def get_detuning_0_index(self):
        if 0.0 in self.detuning:
            detuning_0_index = self.detuning.index(0.0)
        else:
            print(f"Warning: trial does not have data for 0 detuning\n{self.trial_obj}")
            detuning_0_index = 0
        return detuning_0_index

    def get_acceptable_indices(self, data):
        if len(data) > 2:
            acceptable_indices = self.get_acceptable_indices_median(data)
        else:
            acceptable_indices = np.arange(len(data))
        return acceptable_indices

    def get_acceptable_indices_median(self, data):
        deviations = np.abs(data - np.median(data))
        modified_deviation = np.average(deviations**(1/4))**4
        acceptable_indices = np.abs(deviations) < 4 * modified_deviation
        return acceptable_indices

    def filter_deviations(self, acceptable_indices):
        if self.deviations is not None:
            self.deviations = np.array(self.deviations)[acceptable_indices]
