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
        file_contents = [np.array(contents) for contents in zip(*file_contents)]
        if len(file_contents) != 0:
            self.set_detuning_and_greek_from_file(file_contents)
        else:
            print("Warning: no data could be extracted from file in Greek")
            self.detuning, self.drift, self.greek = None, None, None

    def set_detuning_and_greek_from_file(self, file_contents):
        if len(file_contents) == 5:
            self.detuning, self.drift, self.omega, self.gamma, self.amplitude = file_contents
            self.omega_deviation, self.gamma_deviation, self.amplitude_deviations = None, None, None
        else:
            self.detuning, self.drift, self.omega, self.omega_deviation, self.gamma, self.gamma_deviation, self.amplitude, self.amplitude_deviations = file_contents
        self.x_values = self.detuning - self.drift

    def offset_greek_by_0_value(self):
        detuning_0_index = self.get_detuning_0_index()
        self.greek_0_value = self.greek[detuning_0_index]
        self.greek -= self.greek_0_value

    def get_detuning_0_index(self):
        if 0.0 in self.detuning:
            detuning_0_index = np.where(self.detuning == 0.0)[0][0]
        else:
            print(f"Warning: trial does not have data for 0 detuning\n{self.trial_obj}")
            detuning_0_index = 0
        return detuning_0_index
