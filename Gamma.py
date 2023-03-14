import numpy as np

from Greek import Greek

class Gamma(Greek):

    def __init__(self, base_greek):
        self.initialise_from_base_greek(base_greek)
        self.greek = np.abs(base_greek.gamma)
        if hasattr(base_greek, "gamma_deviations"):
            self.deviations = base_greek.gamma_deviations
