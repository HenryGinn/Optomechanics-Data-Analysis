import numpy as np

class GreekLine():

    def __init__(self, greek_child):
        self.detuning = greek_child.detuning
        self.label = greek_child.label
        self.x_values = greek_child.x_values
    
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
