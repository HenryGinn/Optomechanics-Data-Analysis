import numpy as np
import scipy as sc
import math
import matplotlib.pyplot as plt

class DataFit():

    reject_bad_fits = False
    bad_fit_threshold = 20
    parameter_names = ["F", "Gamma", "Noise", "w"]

    def __init__(self, data_obj):
        self.data = data_obj
        self.set_fitting_choice_functions()

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

    def get_initial_fitting_parameters(self):
        noise = self.get_noise()
        resonant = self.get_resonant()
        F, gamma = self.get_F_and_gamma()
        initial_fitting_parameters = [F, gamma, noise, resonant]
        return initial_fitting_parameters

    def get_noise(self):
        end_index = int(len(self.data.S21)/5)
        noise = np.mean(self.data.S21[:end_index])
        return noise

    def get_resonant(self):
        resonant_index = np.argmax(self.data.S21)
        resonant = self.data.frequency[resonant_index]
        return resonant

    def get_F_and_gamma(self):
        width, mid_line_height, approximate_peak = self.get_lorentzian_width_parameters()
        gamma = width * math.sqrt(mid_line_height / (approximate_peak - mid_line_height))
        F = gamma**2 * approximate_peak * 2/3
        return F, gamma

    def get_lorentzian_width_parameters(self):
        approximate_peak, mid_line_height = self.get_lorentzian_height_parameters()
        frequency_resolution = self.data.frequency[1] - self.data.frequency[0]
        peak_points = [self.data.S21 > mid_line_height]
        width = 2 * (np.count_nonzero(peak_points) + 1) * frequency_resolution
        return width, mid_line_height, approximate_peak

    def get_lorentzian_height_parameters(self):
        points_around_peak = self.data.S21[self.data.S21 >= np.max(self.data.S21)*2/3]
        approximate_peak = np.mean(points_around_peak)
        mid_line_height = approximate_peak * 1/2
        return approximate_peak, mid_line_height

    def get_automatic_fit(self, initial_fitting_parameters):
        self.set_fit_data()
        fitting_parameters = sc.optimize.leastsq(self.get_residuals,
                                                 initial_fitting_parameters,
                                                 args=self.data.fit_function)[0]
        return fitting_parameters

    def set_fit_data(self):
        if hasattr(self.data, 'fit_width'):
            self.do_set_fit_data()
        else:
            self.data.fit_frequencies = self.data.frequency
            self.data.fit_S21 = self.data.S21

    def do_set_fit_data(self):
        left = self.get_left_index()
        right = self.get_right_index()
        self.data.fit_frequencies = self.data.frequency[left:right]
        self.data.fit_S21 = self.data.S21[left:right]

    def get_left_index(self):
        left = self.data.peak_index - self.data.fit_width
        if left < 0:
            print(f"Warning: transmission had very off centre peak\n{self.data}")
            left = 0
        return left

    def get_right_index(self):
        right = self.data.peak_index + self.data.fit_width
        if right >= len(self.data.frequency):
            print(f"Warning: transmission had very off centre peak\n{self.data}")
            right = len(self.data.frequency) - 1
        return right

    def get_residuals(self, fitting_parameters, fitting_function):
        residuals = fitting_function(fitting_parameters) - self.data.fit_S21
        return residuals

    def evaluate_lorentzian(self, lorentzian_parameters):
        F, gamma, noise, w = lorentzian_parameters
        function_values = (F/(gamma**2 + 4*(self.data.fit_frequencies - w)**2)) + noise
        return function_values

    def evaluate_polynomial(self, fitting_parameters):
        function_values = np.polyval(fitting_parameters, self.data.fit_frequencies)
        return function_values

    def get_gamma_from_fit(self):
        if self.is_plot_badly_fitted():
            fit_rejected = self.fit_plot_manually_filter()
            if fit_rejected:
                return None
        gamma = abs(self.data.fitting_parameters[1])
        return gamma

    def is_plot_badly_fitted(self):
        fit_heuristic = self.get_fit_heuristic()
        if fit_heuristic > self.bad_fit_threshold:
            if self.reject_bad_fits == False:
                print(f"Fit heuristic: {fit_heuristic}")
            return True
        return False

    def get_fit_heuristic(self):
        fit_ratio = abs(self.data.fitting_parameters[:1]/np.array(self.data.initial_fitting_parameters[:1]))
        fit_heuristic = sum(fit_ratio + 1/fit_ratio)
        return fit_heuristic

    def fit_plot_manually_filter(self):
        if self.reject_bad_fits:
            print("Rejecting fit")
            return None
        else:
            return self.fit_plot_manually()

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
            self.data.fitting_parameters[parameter_index] = new_parameter_value
        except:
            print("Sorry, that didn't work")
        return True, None

    def reset_fitting_parameters(self):
        self.data.fitting_parameters = self.get_initial_fitting_parameters()
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
            self.data.fitting_parameters, input_rejected = self.get_all_fitting_parameters(prompt)
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
        fitting_parameters = self.data.fitting_parameters
        input_wrong = True
        return fitting_parameters, input_wrong

    def check_if_4_fitting_parameters(self, input_rejected):
        if self.data.fitting_parameters is not None:
            if len(self.data.fitting_parameters) != 4:
                input_rejected = True
                print("Sorry, you must enter 4 parameters")
        return input_rejected

    def reattempt_automatic_fit(self):
        self.data.fitting_parameters = self.get_automatic_fit(self.data.fitting_parameters)
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
        parameter_tuples = zip(self.parameter_names, self.data.fitting_parameters)
        for parameter_name, parameter_value in parameter_tuples:
            print(f"{parameter_name}: {parameter_value}")

    def plot_S21(self, fitting=False):
        plt.figure()
        plt.plot(self.data.frequency, self.data.S21, '.', alpha = 1)
        self.plot_fitting(fitting)
        self.add_plot_labels()
        plt.show()

    def plot_fitting(self, fitting):
        if fitting is True and self.data.fitting_parameters is not None:
            self.set_fit_data()
            plt.plot(self.data.fit_frequencies,
                     self.data.fit_function(self.data.fitting_parameters),
                     'k--', alpha=0.5, linewidth=2.0, label='fit')

    def add_plot_labels(self):
        self.add_title()
        self.set_x_ticks_and_labels()
        plt.xlabel(f'Frequency ({self.prefix})')
        plt.ylabel('Amplitude')

    def add_title(self):
        power = self.data.detuning_obj.trial.power_obj.power_string
        trial = self.data.detuning_obj.trial.trial_number
        detuning = self.data.detuning
        plt.title(f"S21 vs Frequency for {power} dBm,\nTrial {trial}, Detuning {detuning} Hz")

    def set_x_ticks_and_labels(self):
        x_ticks = plt.xticks()[0]
        max_x_tick = max(abs(x_ticks))
        prefix_power = math.floor(math.log(max_x_tick, 1000))
        self.prefix = {-1: "mHz", 0: "Hz", 1: "kHz", 2: "MHz", 3: "GHz", 4: "THz"}[prefix_power]
        x_labels = [f'{value:.3f}' for value in plt.xticks()[0]/1000**prefix_power]
        plt.xticks(x_ticks, x_labels)
