import numpy as np
import scipy.optimise as sc

class Fitting():

    def initialise_from_data(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values

    def initialise_from_line_obj(self, line):
        self.x_values = line.x_values
        self.y_values = line.y_values

    def initialise_from_transmission_raw(self, transmission_obj):
        self.x_values = transmission_obj.frequency
        self.y_values = transmission_obj.S21

    def set_fitting_function(self, function_code="Polynomial", args=2):
        set_fitting_function_lookup = {"Polynomial": self.set_fitting_function_polynomial,
                                       "Lorentzian": self.set_fitting_function_lorentzian}
        set_fitting_function_choice = set_fitting_function_lookup[function_code]
        set_fitting_function_choice(*args)

    def set_fitting_function_polynomial(self, *args):
        self.fitting_function = self.evaluate_polynomial
        self.set_polynomial_degree(*args)

    def set_polynomial_degree(self, args):
        if len(args) == 1:
            self.polynomial_degree = args
        else:
            raise Exception((f"Expected 1 argument, got {len(args)}\n"
                             f"Arguments given: {args}"))

    def set_fitting_function_lorentzian(self, *args):
        self.fitting_function = self.evaluate_lorentzian

    def evaluate_polynomial(self, fitting_parameters, x_values=self.x_values):
        function_values = np.polynomial.polynomial.polyval(x_values, fitting_parameters)
        return function_values

    def evaluate_lorentzian(self, fitting_parameters, x_values=self.x_values):
        F, gamma, resonant, noise = fitting_parameters
        function_values = F/(gamma**2 + 4*(x_values - resonant)**2) + noise
        return function_values

    def get_fitting_parameters(self, initial_fitting_parameters=None):
        initial_fitting_parameters = self.get_initial_fitting_parameters(initial_fitting_parameters)
        fitting_parameters = sc.leastsq(self fitting_function, initial_fitting_parameters)

    def get_initial_fitting_parameters(self, initial_fitting_parameters):
        if initial_fitting_parameters is None:
            initial_fitting_parameters = self.do_get_initial_fitting_parameters()
        return initial_fitting_parameters

    def do_get_initial_fitting_parameters(self):
        self.fitting_function_defined()
        functions_dict = self.get_initial_fitting_parameters_functions()
        initial_fitting_parameters = functions_dict[self.fitting_function]()
        return initial_fitting_parameters

    def get_initial_fitting_parameters_functions(self):
        functions_dict = {self.evaluate_polynomial: self.get_initial_fitting_parameters_polynomial,
                          self.evaluate_lorentzian: self.get_initial_fitting_parameters_lorentzian}
        return functions_dict

    def fitting_function_defined(self):
        if hasattr(self, "fitting_function") is False:
            raise Exception(("Fitting function undefined\n"
                             "Call 'set_fitting_function' method of Fitting"))

    def get_initial_fitting_parameters_polynomial(self):
        initial_fitting_parameters = np.zeros(self.polynomial_degree)
        return initial_fitting_parameters

    def get_initial_fitting_parameters_lorentzian(self):
        initial_fitting_parameters = [1e-5, 40, 0, 0]
        return initial_fitting_parameters
        
