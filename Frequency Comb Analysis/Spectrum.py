import numpy as np

from Data import Data

class Spectrum(Data):

    def __init__(self, parent_obj):
        self.parent_obj = parent_obj
    
    def initialise_from_path(self, path):
        Data.__init__(self, self.parent_obj, path)
