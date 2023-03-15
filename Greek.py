import os

import numpy as np
import scipy.optimize as sc

from Utils import get_file_contents

class Greek():

    """
    An instance of this class is a single trend of greek data.
    Each greek file corresponds to one instance, and it is
    managed by GreekFigure
    """

    def __init__(self, trial_obj, greek_obj, label):
        self.trial_obj = trial_obj
        self.greek_obj = greek_obj
        self.label = label

    def extract_from_path(self, path):
        self.path = path
        file_contents = get_file_contents(path)
        self.set_detuning_and_greek(file_contents)

    def set_file_attributes(self, file_name):
        self.file_name = file_name
        self.file_path = os.path.join(self.greek_obj.path, self.file_name)
        
    def set_detuning_and_greek(self, file_contents):
        file_contents = [np.array(contents) for contents in zip(*file_contents)]
        if len(file_contents) != 0:
            self.set_detuning_and_greek_from_file(file_contents)
        else:
            print("Warning: no data could be extracted from file in Greek")
            self.detuning, self.drift, self.greek = None, None, None

    def set_detuning_and_greek_from_file(self, file_contents):
        if len(file_contents) == 5:
            self.detuning, self.drift, self.omega, self.gamma, self.amplitude = file_contents
            self.omega_deviation, self.gamma_deviation, self.amplitude_deviations = None, None, None
        else:
            self.detuning, self.drift, self.omega, self.omega_deviation, self.gamma, self.gamma_deviation, self.amplitude, self.amplitude_deviations = file_contents
        self.x_values = self.detuning - self.drift
    
    def offset_omega_by_0_value(self):
        detuning_0_index = self.get_detuning_0_index()
        self.omega_0_value = self.omega[detuning_0_index]
        self.omega -= self.omega_0_value

    def get_detuning_0_index(self):
        if 0.0 in self.detuning:
            detuning_0_index = np.where(self.detuning == 0.0)[0][0]
        else:
            print(f"Warning: trial does not have data for 0 detuning\n{self.trial_obj}")
            detuning_0_index = 0
        return detuning_0_index

    def get_omega_fitting_parameters(self):
        initial_fitting_parameters = [1000, 1]
        omega_fitting_parameters = sc.leastsq(self.get_residuals_omega,
                                              initial_fitting_parameters)[0]
        return omega_fitting_parameters

    def get_residuals_omega(self, fitting_parameters):
        function_values = self.evaluate_omega_curve(fitting_parameters)
        residuals = function_values - self.omega
        return residuals

    def evaluate_omega_curve(self, fitting_parameters):
        g, kappa = fitting_parameters
        coefficient = g**2 * np.sign(self.x_values)
        plus = self.detuning + self.omega
        minus = self.detuning - self.omega
        term_plus = plus/(plus**2 + kappa**2/4)
        term_minus = minus/(minus**2 + kappa**2/4)
        function_values = coefficient*(term_plus + term_minus)
        return function_values

    def get_gamma_fitting_parameters(self):
        initial_fitting_parameters = [40, 1000000, 500]
        gamma_fitting_parameters = sc.leastsq(self.get_residuals_gamma,
                                              initial_fitting_parameters)[0]
        gamma_fitting_parameters = initial_fitting_parameters
        return gamma_fitting_parameters

    def get_residuals_gamma(self, fitting_parameters):
        function_values = self.evaluate_gamma_curve(fitting_parameters)
        residuals = function_values - self.gamma
        return residuals

    def evaluate_gamma_curve(self, fitting_parameters):
        gamma_0, g, kappa = fitting_parameters
        coefficient = g**2 * np.sign(self.x_values)
        plus = self.x_values + self.omega + self.omega_0_value
        minus = self.x_values - self.omega - self.omega_0_value
        term_plus = kappa/(plus**2 + kappa**2/4)
        term_minus = kappa/(minus**2 + kappa**2/4)
        function_values = gamma_0 + coefficient*(term_plus - term_minus)
        return function_values
