import numpy as np

from Greek import Greek

class Amplitude(Greek):

    def __init__(self, base_greek):
        self.initialise_from_base_greek(base_greek)
        self.greek = np.abs(base_greek.amplitude)
        if hasattr(base_greek, "amplitude_deviations"):
            self.deviations = base_greek.amplitude_deviations
