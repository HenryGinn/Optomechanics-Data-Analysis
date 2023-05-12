import math

import numpy as np
import scipy.optimize as sc

from Utils import evaluate_lorentzian

class TransmissionFittingParameters():

    # kappa_ext, kappa_tot
    #parameters_dict = {"24": (16965779.6, 26505841.9),
    #                   "25": (16884359.9, 26415157.0),
    #                   "26": (16773538.6, 26288609.2),
    #                   "27": (16616858.7, 26141769.8),
    #                   "28": (16415232.3, 25818528.8),
    #                   "29": (18086263.1, 25508271.9)}
    parameters_dict = {"24": (3.72*10**12, 2.6*10**7),
                       "25": (4.4*10**12, 2.6*10**7),
                       "26": (4.6*10**12, 2.6*10**7),
                       "27": (5.6*10**12, 2.6*10**7),
                       "28": (3.72*10**12, 2.6*10**7),
                       "29": (3.72*10**12, 2.6*10**7)}


    def __init__(self, transmission_obj):
        self.transmission_obj = transmission_obj
        self.frequency = transmission_obj.frequency
        self.S21 = transmission_obj.S21

    def set_fitting_parameters(self):
        self.set_fixed_fitting_parameters()
        initial_resonant = self.frequency[np.argmax(self.S21)]
        self.fitting_parameters = self.get_automatic_fitting_parameters(initial_resonant)
        print(self.fitting_parameters)

    def set_fixed_fitting_parameters(self):
        power = self.transmission_obj.detuning_obj.trial_obj.power_obj.power_string
        F, gamma = self.parameters_dict[power]
        noise = 0
        self.fixed_fitting_parameters = (F, gamma, noise)

    def get_automatic_fitting_parameters(self, initial_resonant):
        resonant = sc.leastsq(self.get_residuals,
                              initial_resonant)[0]
        fitting_parameters = (*self.fixed_fitting_parameters, resonant)
        return fitting_parameters

    def get_residuals(self, resonant):
        x_values = self.frequency
        fitting_parameters = (*self.fixed_fitting_parameters, resonant[0])
        function_values = evaluate_lorentzian(x_values, fitting_parameters)
        residuals = function_values - self.S21
        return residuals

    def get_automatic_fitting_parameters2(self, resonant):
        fitting_parameters = (*self.fixed_fitting_parameters, resonant)
        fitting_parameters = sc.leastsq(self.get_residuals2,
                                        fitting_parameters)[0]
        return fitting_parameters

    def get_residuals2(self, fitting_parameters):
        x_values = self.frequency
        function_values = evaluate_lorentzian(x_values, fitting_parameters)
        residuals = function_values - self.S21
        return residuals


def get_transmission_fitting_parameters(transmission_obj):
    fitting_parameters_obj = TransmissionFittingParameters(transmission_obj)
    fitting_parameters_obj.set_fitting_parameters()
    return fitting_parameters_obj.fitting_parameters

def residuals(p, X ,f):
    function_values = evaluate(p, f)
    res = (function_values - X)
    return res
