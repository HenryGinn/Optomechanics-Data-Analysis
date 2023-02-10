from Data import Data
import os
import numpy as np

class Spectrum(Data):

    """
    This class handles all the data for one spectrum of one detuning for one trial.
    """
    
    def __init__(self, detuning_obj, spectrum_path):
        Data.__init__(self, detuning_obj, spectrum_path)
        

class Transmission(Data):

    """
    This class handles all the data for the transmission of one detuning for one trial.
    """
    
    def __init__(self, detuning_obj, transmission_path):
        Data.__init__(self, detuning_obj, transmission_path)
