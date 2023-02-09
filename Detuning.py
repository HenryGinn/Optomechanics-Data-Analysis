import numpy as np
import matplotlib.pyplot as plt
import math
import scipy as sc
from Spectrum import Spectrum

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class Detuning():

    """
    This class handles all the data for one detuning for one trial.
    Processing of spectra happens here.
    """

    parameter_names = ["F", "Gamma", "Noise", "w"]
    bad_fit_threshold = 20
    
    def __init__(self, trial, detuning, timestamp, transmission_path, spectrum_paths):
        self.initialise_attributes(trial, detuning, timestamp,
                                   transmission_path, spectrum_paths)
        self.set_frequency()
        self.create_spectrum_objects()
        self.set_fitting_choice_functions()

    def initialise_attributes(self, trial, detuning, timestamp,
                              transmission_path, spectrum_paths):
        self.trial = trial
        self.detuning = detuning
        self.timestamp = timestamp
        self.transmission_path = transmission_path
        self.spectrum_paths = spectrum_paths

    def set_frequency(self):
        with open(self.spectrum_paths[0], "r") as file:
            file.readline()
            self.frequency = np.array([self.get_frequency_from_file_line(line)
                                       for line in file])

    def get_frequency_from_file_line(self, line):
        line_components = line.strip().split("\t")
        try:
            frequency = float(line_components[1])
            return frequency
        except:
            raise Exception((f"Could not read frequency from file line '{line}'"
                             f"while attempting to process detuning:\n{self}"))

    def create_spectrum_objects(self):
        self.spectrum_objects = [Spectrum(self, spectrum_path)
                                 for spectrum_path in self.spectrum_paths]

    def set_fitting_choice_functions(self):
        self.fitting_choice_functions = {"1": (self.update_fitting_parameter, 0),
                                         "2": (self.update_fitting_parameter, 1),
                                         "3": (self.update_fitting_parameter, 2),
                                         "4": (self.update_fitting_parameter, 3),
                                         "5": (self.reset_fitting_parameters, ),
                                         "6": (self.update_all_fitting_parameters, ),
                                         "7": (self.reattempt_automatic_fit, ),
                                         "8": (self.accept_fit, ),
                                         "": (self.reject_fit, )}

    def process_transmission(self):
        self.transmission = Spectrum(self, self.transmission_path)
        self.transmission.process_spectrum()

    def process_S21(self):
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.process_spectrum()
        self.set_S21_and_frequency_offset()
        self.S21 = np.mean([spectrum_obj.S21_offset
                            for spectrum_obj in self.spectrum_objects], axis=0)
    
    def set_gamma(self):
        self.set_average_S21()
        self.initial_fitting_parameters = self.get_initial_fitting_parameters()
        self.fitting_parameters = self.get_automatic_fit(self.initial_fitting_parameters)
        self.gamma = self.get_gamma_from_fit()

    def set_S21_and_frequency_offset(self):
        self.set_centre_indexes()
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.set_S21_offset()
        self.set_frequency_offset()

    def set_centre_indexes(self):
        self.spectrum_centre_indexes = [spectrum_obj.S21_centre_index
                                        for spectrum_obj in self.spectrum_objects]
        self.min_centre_index = min(self.spectrum_centre_indexes)
        self.max_centre_index = max(self.spectrum_centre_indexes)

    def plot_peak_S21_drift(self):
        plt.plot(self.frequency[np.array(self.spectrum_centre_indexes)])
        plt.xlabel("Spectrum number")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Frequency of Peak S21 vs Spectrum\n"
                   f"Number at {self.trial.power_obj.power_string} dBm"))
        plt.show()

    def set_frequency_offset(self):
        cutoff_size = self.max_centre_index - self.min_centre_index
        frequency_offset_length = len(self.frequency) - cutoff_size
        self.frequency_offset = np.copy(self.frequency[:frequency_offset_length])
        self.frequency_offset -= self.frequency_offset[self.min_centre_index]

    def get_initial_fitting_parameters(self):
        end = int(len(self.S21)/5)
        noise, w = np.mean(self.S21[:end])/20, 2
        K = np.mean(self.S21[self.S21 >= np.max(self.S21)*2/3])
        k = K * 1/3
        frequency_resolution = self.frequency[1] - self.frequency[0]
        peak_points = [self.S21 > k]
        width = 2 * (np.count_nonzero(peak_points) + 1)/frequency_resolution
        gamma = width * math.sqrt(k/(K-k))
        F = gamma**2 * K * 1/2
        initial_fitting_parameters = [F, gamma, noise, w]
        return initial_fitting_parameters

    def get_automatic_fit(self, initial_fitting_parameters):
        fitting_parameters = sc.optimize.leastsq(self.get_residuals,
                                                 initial_fitting_parameters)[0]
        return fitting_parameters

    def get_residuals(self, fitting_parameters):
        residuals = self.evaluate_lorentzian(fitting_parameters) - self.S21
        return residuals

    def evaluate_lorentzian(self, lorentzian_parameters):
        F, gamma, noise, w = lorentzian_parameters
        function_values = (F/(gamma**2 + 4*(self.frequency_offset - w)**2)) + noise
        return function_values

    def get_gamma_from_fit(self):
        if self.is_plot_badly_fitted():
            fit_rejected = self.fit_plot_manually()
            if fit_rejected:
                return None
        gamma = self.fitting_parameters[1]
        return gamma

    def is_plot_badly_fitted(self):
        fit_heuristic = self.get_fit_heuristic()
        if fit_heuristic > self.bad_fit_threshold:
            print(f"Fit heuristic: {fit_heuristic}")
            return True
        return False

    def get_fit_heuristic(self):
        fit_ratio = self.fitting_parameters[:2]/np.array(self.initial_fitting_parameters[:2])
        fit_heuristic_multiplicative = sum(fit_ratio + 1/fit_ratio)
        fit_heuristic_additive = abs(self.fitting_parameters[3] - self.initial_fitting_parameters[3])
        fit_heuristic = fit_heuristic_multiplicative + fit_heuristic_additive
        return fit_heuristic

    def fit_plot_manually(self):
        continue_looping = True
        while continue_looping:
            self.output_fitting_parameters()
            self.plot_S21(fitting = True)
            continue_looping, fit_rejected = self.fit_plot_manually_iteration()

    def fit_plot_manually_iteration(self):
        fitting_input_choice = self.get_fitting_input_choice()
        continue_looping, fit_rejected = self.execute_manual_fit_choice(fitting_input_choice)
        return continue_looping, fit_rejected

    def get_fitting_input_choice(self):
        prompt = ("\nWhich option do you want to change?\n1: F\n2: Gamma\n3: Noise\n" +
                  "4: w\n5: Reset to default\n6: Change all at once\n" +
                  "7: Attempt automatic fit\n8: Accept\nNo input: Reject\n")
        fitting_input_choice = input(prompt)
        return fitting_input_choice

    def execute_manual_fit_choice(self, fitting_input_choice):
        if fitting_input_choice in self.fitting_choice_functions:
            a = self.fitting_choice_functions[fitting_input_choice]
            fitting_choice_function, *args = self.fitting_choice_functions[fitting_input_choice]
            continue_looping, fit_rejected = fitting_choice_function(*args)
        else:
            print("Sorry, you must choose one of the options. Try again.")
            continue_looping, fit_rejected = True, None
        return continue_looping, fit_rejected

    def update_fitting_parameter(self, parameter_index):
        parameter_index = int(parameter_index)
        prompt = f"\nWhat is the new value of '{self.parameter_names[parameter_index]}': "
        try:
            new_parameter_value = float(input(prompt))
            self.fitting_parameters[parameter_index] = new_parameter_value
        except:
            print("Sorry, that didn't work")
        return True, None

    def reset_fitting_parameters(self):
        self.fitting_parameters = self.get_initial_fitting_parameters()
        continue_looping = True
        fit_rejected = None
        return continue_looping, fit_rejected

    def update_all_fitting_parameters(self):
        prompt = "Enter all the new values in a list separated by spaces\n"
        self.set_all_fitting_parameters(prompt)
        continue_looping = True
        fit_rejected = None
        return continue_looping, fit_rejected

    def set_all_fitting_parameters(self, prompt):
        input_rejected = True
        while input_rejected:
            self.fitting_parameters, input_rejected = self.get_all_fitting_parameters(prompt)
            input_rejected = self.check_if_4_fitting_parameters(input_rejected)

    def get_all_fitting_parameters(self, prompt):
        try:
            fitting_parameters, input_wrong = self.attempt_get_fitting_parameters(prompt)
        except:
            fitting_parameters, input_wrong = self.failed_attempt_fitting_parameters()
        return fitting_parameters, input_wrong

    def attempt_get_fitting_parameters(self, prompt):
        fitting_parameters = [float(parameter_input)
                              for parameter_input in input(prompt).split(" ")]
        input_wrong = False
        return fitting_parameters, input_wrong

    def failed_attempt_fitting_parameters(self):        
        print("Sorry, you typed it in wrong, try again")
        fitting_parameters = self.fitting_parameters
        input_wrong = True
        return fitting_parameters, input_wrong

    def check_if_4_fitting_parameters(self, input_rejected):
        if self.fitting_parameters is not None:
            if len(self.fitting_parameters) != 4:
                input_rejected = True
                print("Sorry, you must enter 4 parameters")
        return input_rejected

    def reattempt_automatic_fit(self):
        self.fitting_parameters = self.get_automatic_fit(self.fitting_parameters)
        continue_looping = True
        fit_rejected = None
        return continue_looping, fit_rejected

    def accept_fit(self):
        continue_looping = False
        fit_rejected = False
        return continue_looping, fit_rejected

    def reject_fit(self):
        continue_looping = False
        fit_rejected = True
        return continue_looping, fit_rejected

    def output_fitting_parameters(self):
        parameter_tuples = zip(self.parameter_names, self.fitting_parameters)
        for parameter_name, parameter_value in parameter_tuples:
            print(f"{parameter_name}: {parameter_value}")

    def plot_S21(self, fitting=False):
        plt.figure()
        plt.plot(self.frequency_offset, self.S21, '.', alpha = 1)
        self.plot_fitting(fitting)
        self.add_plot_labels()
        plt.show()

    def plot_fitting(self, fitting):
        if fitting is True and self.fitting_parameters is not None:
            plt.plot(self.frequency_offset,
                     self.evaluate_lorentzian(self.fitting_parameters),
                     'k--', alpha=0.5, linewidth=2.0, label='fit')

    def add_plot_labels(self):
        plt.title("My Title")
        x_ticks = plt.xticks()[0]
        max_x_tick = max(abs(x_ticks))
        prefix_power = math.floor(math.log(max_x_tick, 1000))
        prefix = {-1: "mHz", 0: "Hz", 1: "kHz", 2: "MHz", 3: "GHz", 4: "THz"}[prefix_power]
        x_labels = [f'{value:.0f}' for value in plt.xticks()[0]/1000**prefix_power]
        plt.xticks(x_ticks, x_labels)
        plt.xlabel('${\omega_c}$' + f'({prefix})')
        plt.ylabel('Amplitude')

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"Power: {self.trial.power_obj.power_string}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum paths count: {len(self.spectrum_paths)}\n")
        return string
