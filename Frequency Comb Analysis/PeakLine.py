import numpy as np
import scipy.optimize as sc

class PeakLine():

    def __init__(self, fit_peak_obj, x_values, y_values, name):
        self.fit_peak_obj = fit_peak_obj
        self.x_values = x_values
        self.y_values = y_values
        self.name = name

    def fit_line(self):
        self.set_initial_fitting_parameters()
        self.fitting_parameters = sc.leastsq(self.get_line_residuals,
                                             self.initial_fitting_parameters)[0]

    def set_initial_fitting_parameters(self):
        point_1, point_2, point_difference = self.get_points()
        gradient = point_difference["y"] / point_difference["x"]
        y_intercept = point_difference["x"]*point_1["x"] - point_difference["y"]*point_1["y"]
        self.initial_fitting_parameters = [gradient, y_intercept]

    def get_points(self):
        point_1 = {"x": self.x_values[0], "y": self.y_values[0]}
        point_2 = {"x": self.x_values[-1], "y": self.y_values[-1]}
        point_difference = {"x": point_1["x"] - point_2["x"],
                            "y": point_1["y"] - point_2["y"]}
        return point_1, point_2, point_difference

    def get_line_residuals(self, fitting_parameters):
        function_values = self.evaluate_line(self.x_values, fitting_parameters)
        residuals = function_values - self.y_values
        return residuals

    def evaluate_line(self, x_values, fitting_parameters):
        gradient, y_intercept = fitting_parameters
        function_values = gradient*x_values + y_intercept
        return function_values

    def set_values_fit(self):
        self.x_values_fit = np.array([self.x_values[0], self.x_values[-1]])
        self.y_values_fit = self.evaluate_line(self.x_values_fit,
                                               self.fitting_parameters)
        self.y_values_fit = np.exp(self.y_values_fit)
