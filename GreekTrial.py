import numpy as np
import os
from Greek import Greek

class GreekTrial():

    def __init__(self, trial_obj):
        self.trial = trial_obj

    def set_trial_from_file(self):
        self.trial.set_transmission()
        self.trial.set_spectrum()

    def get_label_from_average_size(self, average_size):
        if average_size is None:
            label = "AllSpectraAveraged"
        else:
            label = str(average_size)
        return label
    
    def set_files(self):
        self.files = self.trial.get_data_files(self.path)

    def set_children(self):
        self.children = [self.get_child(file_name)
                         for file_name in self.files]

    def get_child(self, file_name):
        label = self.get_label(file_name)
        child = Greek(self.trial, self, label)
        child.extract_from_file(file_name)
        return child
    
    def get_label_from_file_name(self, file_name):
        label = file_name[file_name.index("l") + 4:-4]
        if label == "":
            label = "NoLabel"
        return label
