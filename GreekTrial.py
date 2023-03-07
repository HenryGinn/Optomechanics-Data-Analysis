import numpy as np
import os

class GreekTrial():

    def __init__(self, trial_obj):
        self.trial = trial_obj
    
    def get_label(self, file_name):
        label = file_name[file_name.index("l") + 4:-4]
        if label == "":
            label = "All used\nin average"
        return label
