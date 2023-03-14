import numpy as np

from Greek import Greek

class Omega(Greek):

    def __init__(self, base_greek):
        self.initialise_from_base_greek(base_greek)
        self.greek = np.abs(base_greek.omega)
        self.offset_greek_by_0_value()
        if hasattr(base_greek, "omega_deviations"):
            self.deviations = base_greek.omega_deviations
