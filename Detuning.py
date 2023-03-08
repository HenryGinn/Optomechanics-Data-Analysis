import numpy as np
import matplotlib.pyplot as plt
import math
from Spectrum import Spectrum
from Transmission import Transmission
from AverageDetuning import AverageDetuning
from Utils import get_number_from_file_name

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class Detuning():

    """
    This class handles all the data for one detuning for one trial.
    Processing of spectra happens here.
    """

    output_rejected_spectra = False
    flag_bad_offsets = False
    
    def __init__(self, trial, detuning, timestamp, transmission_path, spectrum_paths):
        self.initialise_attributes(trial, detuning, timestamp,
                                   transmission_path, spectrum_paths)
        self.valid = True
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
        self.cavity_frequency = get_number_from_file_name(self.spectrum_paths[0], "cavity_freq")

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

    def get_transmission_peak(self):
        self.process_transmission()
        if self.transmission.peak_not_off_centre:
            return (self.transmission.S21_centre_index,
                    self.transmission.S21_centre_frequency)
        else:
            return None, None

    def process_transmission(self):
        self.transmission = Transmission(self, self.transmission_path)
        self.transmission.process_S21()

    def extract_transmission_from_file_detuning(self, centre_index, centre_frequency, cavity_frequency):
        self.transmission = Transmission(self, self.transmission_path)
        self.transmission.S21_centre_index = centre_index
        self.transmission.S21_centre_frequency = centre_frequency
        self.cavity_frequency = cavity_frequency

    def get_spectrum_peaks(self):
        self.process_spectrum()
        self.set_valid_spectrum_indexes()
        self.filter_bad_offsets()
        spectrum_centre_indexes, spectrum_centre_frequencies = self.get_centre_information()
        return spectrum_centre_indexes, spectrum_centre_frequencies, self.valid_spectrum_indexes

    def process_spectrum(self):
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.process_S21()

    def set_valid_spectrum_indexes(self):
        self.valid_spectrum_indexes = [spectrum_obj.S21_has_valid_peak
                                       for spectrum_obj in self.spectrum_objects]
        self.valid_spectrum_indexes = np.array(self.valid_spectrum_indexes)
        self.valid_spectrum_indexes = np.nonzero(self.valid_spectrum_indexes)[0]

    def filter_bad_offsets(self):
        spectrum_centres = self.get_spectrum_centre_indexes()
        acceptable_indexes = get_acceptable_indexes(spectrum_centres, 5)
        self.output_rejected_spectrum_data(acceptable_indexes)
        self.valid_spectrum_indexes = self.valid_spectrum_indexes[acceptable_indexes]
        self.update_valid_peaks(self.valid_spectrum_indexes)

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

    def extract_spectrum_from_file_detuning(self, spectrum_file_contents):
        properties = [(centre_indexes, centre_frequencies, indexes) for
                      detuning, centre_indexes, centre_frequencies, indexes in spectrum_file_contents
                      if detuning == self.detuning]
        self.set_spectra_properties_from_file(properties)

    def set_spectra_properties_from_file(self, variables):
        if variables != []:
            self.set_spectra_properties_from_file_valid(variables)
        else:
            self.valid = False

    def set_spectra_properties_from_file_valid(self, variables):
        centre_indexes, centre_frequencies, indexes = zip(*variables)
        self.spectrum_centre_indexes = np.array(centre_indexes)
        self.spectrum_centre_frequencies = np.array(centre_frequencies)
        self.spectrum_indexes = np.array(indexes).astype("int")
        self.set_spectrum_objects_valid()

    def set_spectrum_objects_valid(self):
        self.spectrum_objects_valid = [spectrum_obj
                                       for index, spectrum_obj in enumerate(self.spectrum_objects)
                                       if index in self.spectrum_indexes]
        self.update_spectrum_valid_peaks()
        self.set_spectrum_objects_centre_data()
        self.set_spectrum_objects_S21()

    def update_spectrum_valid_peaks(self):
        for spectrum_obj in self.spectrum_objects:
            if spectrum_obj in self.spectrum_objects_valid:
                spectrum_obj.S21_has_valid_peak = True
            else:
                spectrum_obj.S21_has_valid_peak = False

    def set_spectrum_objects_centre_data(self):
        spectrum_centre_zip = zip(self.spectrum_objects_valid,
                                  self.spectrum_centre_indexes,
                                  self.spectrum_centre_frequencies)
        for spectrum_obj, centre_index, centre_frequency in spectrum_centre_zip:
            spectrum_obj.S21_centre_index = int(centre_index)
            spectrum_obj.S21_centre_frequency = centre_frequency

    def set_spectrum_objects_S21(self):
        for spectrum_obj in self.spectrum_objects_valid:
            spectrum_obj.set_S21()

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

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"Power: {self.trial.power_obj.power_string}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum paths count: {len(self.spectrum_paths)}\n"
                  f"Valid: {self.valid}\n")
        return string
