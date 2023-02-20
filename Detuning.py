import numpy as np
import matplotlib.pyplot as plt
import math
from DataTypes import *

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class Detuning():

    """
    This class handles all the data for one detuning for one trial.
    Processing of spectra happens here.
    """

    parameter_names = ["F", "Gamma", "Noise", "w"]
    output_rejected_spectra = False
    bad_fit_threshold = 20
    flag_bad_offsets = False
    
    def __init__(self, trial, detuning, timestamp, transmission_path, spectrum_paths):
        self.initialise_attributes(trial, detuning, timestamp,
                                   transmission_path, spectrum_paths)
        self.set_frequency()
        self.create_spectrum_objects()

    def initialise_attributes(self, trial, detuning, timestamp,
                              transmission_path, spectrum_paths):
        self.trial = trial
        self.detuning = detuning
        self.timestamp = timestamp
        self.transmission_path = transmission_path
        self.spectrum_paths = spectrum_paths

    def set_frequency(self):
        self.set_spectrum_frequency()
        self.cavity_frequency = self.trial.get_number_from_file_name(self.spectrum_paths[0], "cavity_freq")

    def set_spectrum_frequency(self):
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

    def process_transmission(self):
        self.transmission = Transmission(self, self.transmission_path)
        self.transmission.process_S21()
        self.transmission.set_S21_centre_index()
        self.actual_frequency = self.transmission.S21_centre_frequency

    def get_S21_peaks(self):
        self.process_S21()
        self.set_valid_spectrum_indexes()
        self.filter_bad_offsets()
        spectrum_centre_indexes, spectrum_centre_frequencies = self.get_centre_information()
        return spectrum_centre_indexes, spectrum_centre_frequencies, self.valid_spectrum_indexes

    def process_S21(self):
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.process_S21()

    def set_valid_spectrum_indexes(self):
        self.valid_spectrum_indexes = [spectrum_obj.S21_has_valid_peak
                                       for spectrum_obj in self.spectrum_objects]
        self.valid_spectrum_indexes = np.array(self.valid_spectrum_indexes)
        self.valid_spectrum_indexes = np.nonzero(self.valid_spectrum_indexes)[0]

    def filter_bad_offsets(self):
        spectrum_centres = self.get_spectrum_centre_indexes()
        acceptable_indexes = self.get_acceptable_indexes(spectrum_centres,
                                                         self.valid_spectrum_indexes, 5)
        self.output_rejected_spectrum_data(acceptable_indexes)
        self.update_valid_peaks(acceptable_indexes)
        self.valid_spectrum_indexes = acceptable_indexes

    def output_rejected_spectrum_data(self, acceptable_indexes):
        if self.output_rejected_spectra:
            print(f"Detuing: {self.detuning}, "
                  f"total spectra: {len(self.spectrum_objects)}, "
                  f"bad peak: {len(self.spectrum_objects) - len(self.valid_spectrum_indexes)}, "
                  f"bad offset: {len(self.valid_spectrum_indexes) - len(acceptable_indexes)}, "
                  f"remaining: {len(acceptable_indexes)}")

    def update_valid_peaks(self, acceptable_indexes):
        for index in self.valid_spectrum_indexes:
            if index not in acceptable_indexes:
                self.spectrum_objects[index].S21_has_valid_peak = False

    def set_spectrum_properties_from_file(self, variables):
        if variables != []:
            self.valid = True
            self.set_spectrum_properties_from_file_valid(variables)
        else:
            self.valid = False

    def set_spectrum_properties_from_file_valid(self, variables):
        centre_indexes, centre_frequencies, indexes = zip(*variables)
        self.spectrum_centre_indexes = np.array(centre_indexes)
        self.spectrum_centre_frequencies = np.array(centre_frequencies)
        self.spectrum_indexes = np.array(indexes).astype("int")
        self.set_spectrum_object_properties_from_file()

    def set_spectrum_object_properties_from_file(self):
        for index in self.spectrum_indexes:
            spectrum_obj = self.spectrum_objects[index]
            #print(dir(spectrum_obj))

    def set_S21_and_frequency_offset(self):
        self.min_centre_index = min(self.spectrum_centre_indexes)
        self.max_centre_index = max(self.spectrum_centre_indexes)
        self.is_offset_reasonable()
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.set_S21_offset()
        self.set_frequency_offset()

    def get_centre_information(self):
        spectrum_centre_indexes = self.get_spectrum_centre_indexes()
        spectrum_centre_frequencies = self.get_spectrum_centre_frequencies()
        return spectrum_centre_indexes, spectrum_centre_frequencies

    def get_spectrum_centre_indexes(self):
        spectrum_centre_indexes = [spectrum_obj.get_S21_centre_index()
                                   for spectrum_obj in self.spectrum_objects
                                   if spectrum_obj.S21_has_valid_peak]
        spectrum_centre_indexes = np.array(spectrum_centre_indexes)
        return spectrum_centre_indexes

    def get_spectrum_centre_frequencies(self):
        spectrum_centre_frequencies = [spectrum_obj.get_S21_centre_frequency()
                                       for index, spectrum_obj in enumerate(self.spectrum_objects)
                                       if spectrum_obj.S21_has_valid_peak]
        spectrum_centre_frequencies = np.array(spectrum_centre_frequencies)
        return spectrum_centre_frequencies

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

    def get_omegas_all(self):
        centre_frequencies = self.spectrum_centre_frequencies
        omegas_all = centre_frequencies - self.cavity_frequency - self.detuning
        acceptable_indexes = self.get_acceptable_indexes(omegas_all)
        self.spectrum_indexes = self.spectrum_indexes[acceptable_indexes]
        omegas_all = omegas_all[acceptable_indexes]
        drifts = self.get_drifts(self.spectrum_indexes, len(self.spectrum_objects))
        return omegas_all, drifts

    def get_acceptable_indexes(self, data, tolerance = 4):
        if data.size < 3:
            acceptable_indexes = np.arange(len(data))
        else:
            acceptable_indexes = self.get_acceptable_indexes_non_trivial(data, tolerance)
        return acceptable_indexes

    def get_data_filtered(self, data, tolerance = 4):
        acceptable_indexes = self.get_acceptable_indexes_non_trivial(data, tolerance)
        data_filtered = data[accepted_indexes]
        return data_filtered

    def get_acceptable_indexes_non_trivial(self, data, tolerance):
        deviations = np.abs(data - np.median(data))
        modified_deviation = np.average(deviations**(1/4))**4
        accepted_indexes = np.abs(deviations) < tolerance * modified_deviation
        return accepted_indexes

    def get_drifts(self, indexes, total):
        spacings = indexes / total
        current_detuning = self.actual_frequency
        next_detuning = self.next_detuning.actual_frequency
        difference = next_detuning - current_detuning
        drifts = difference*spacings
        return drifts

    def get_omegas_averages(self, average_size):
        drifts_all, omegas_all = self.get_omegas_all_from_file()
        average_size = self.get_average_size(average_size, len(omegas_all))
        omegas_averages = self.average_list(omegas_all, average_size)
        drifts_averages = self.average_list(drifts_all, average_size)
        return omegas_averages, drifts_averages

    def get_omegas_all_from_file(self):
        with open(self.trial.omega_all_file_path, "r") as file:
            file.readline()
            file_contents = [[float(value) for value in line.strip().split("\t")]
                              for line in file]
            drifts, omegas = self.get_drift_and_omega_from_file(file_contents)
        return drifts, omegas

    def get_drift_and_omega_from_file(self, file_contents):
        drifts_and_omegas = [(drift, omega) for detuning, drift, omega in file_contents
                             if detuning == self.detuning]
        drifts, omegas = zip(*drifts_and_omegas)
        drifts = np.array(drifts)
        omegas = np.array(omegas)
        return drifts, omegas

    def get_average_size(self, average_size, total_count):
        if average_size is None:
            average_size = total_count
        return average_size

    def average_list(self, list_full, average_size):
        group_indexes = self.get_group_indexes(len(list_full), average_size)
        list_averages = [np.mean(list_full[indexes], axis = 0)
                         for indexes in group_indexes]
        return list_averages
    
    def get_group_indexes(self, length, group_size):
        group_size = self.get_modified_group_size(length, group_size)
        group_count = math.floor(length/group_size)
        real_group_size = length/group_count
        end_point_indexes = np.ceil(np.arange(0, group_count + 1) * real_group_size)
        group_indexes = [np.arange(end_point_indexes[group_number],
                                   end_point_indexes[group_number + 1]).astype('int')
                         for group_number in range(group_count)]
        return group_indexes

    def get_modified_group_size(self, list_size, average_size):
        if list_size < average_size:
            average_size = list_size
        return average_size
    
    def set_gamma_averages(self, average_size):
        average_size = self.get_average_size(average_size, len(self.spectrum_objects))
        S21_averages = self.get_S21_averages(average_size)
        print(S21_averages)
        self.initial_fitting_parameters = self.get_initial_fitting_parameters(self.frequency, self.S21)
        self.fitting_parameters = self.get_automatic_fit(self.initial_fitting_parameters)
        self.gamma = self.get_gamma_from_fit()

    def get_S21_averages(self, average_size):
        for index in self.spectrum_indexes:
            spectrum_obj = self.spectrum_objects[index]
            spectrum_obj.set_S21()
            print(spectrum_obj.S21)
        input()
        return S21_averages

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

    def plot_omegas(self, omegas):
        plt.plot(omegas)
        plt.title(f"Omega vs Spectrum Number for {self.trial.power_obj.folder_name}, {self.detuning} Hz")
        plt.xlabel("Spectrum Number")
        plt.ylabel("Frequency (Hz)")
        plt.show()

    def create_detuning_plots(self, plot_name):
        {"Frequency of peak": self.plot_frequency_of_peak}[plot_name]()

    def plot_frequency_of_peak(self):
        peak_frequencies = [spectrum_obj.S21_centre_frequency
                            for spectrum_obj in self.spectrum_objects]
        print(self.spectrum_objects[0])
        plt.plot(peak_frequencies)
        self.add_frequency_of_peak_labels()
        plt.show()

    def add_frequency_of_peak_labels(self):
        plt.xlabel("Spectrum number")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Peak Frequency vs Spectrum Number\n"
                   f"for {self.trial.power_obj.folder_name}, {self.detuning} Hz"))

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"Power: {self.trial.power_obj.power_string}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum paths count: {len(self.spectrum_paths)}\n")
        return string
