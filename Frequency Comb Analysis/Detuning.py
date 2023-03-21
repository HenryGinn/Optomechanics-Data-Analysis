import sys
sys.path.append("..")

import numpy as np

from Group import Group

class Detuning():

    def __init__(self, drift_obj, detuning, paths):
        self.drift_obj = drift_obj
        self.detuning = detuning
        self.paths = paths
        self.process_detuning()

    def process_detuning(self):
        self.drift = self.drift_obj.drift
        self.set_group_objects()
        self.group_size = len(self.group_objects)
        self.set_timestamps()

    def set_group_objects(self):
        self.group_objects = np.array([Group(self, path)
                                       for path in self.paths])

    def set_timestamps(self):
        self.timestamps = [group.timestamp for group in self.group_objects]

    def process_spectrum(self):
        for group_obj in self.group_objects:
            group_obj.process_spectrum()

    def __str__(self):
        string = f"{self.drift_obj}, Detuning {self.detuning}"
        return string
