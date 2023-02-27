import matplotlib.pyplot as plt
import os
from PlotGammaAndOmega import PlotGreek
from DetuningPlot import DetuningPlot

class TrialPlot():

    def __init__(self, trial_obj):
        self.trial = trial_obj

    def plot_omega_and_gamma(self, format_type):
        self.greek_fig, (self.axis_omega, self.axis_gamma) = plt.subplots(2)
        self.plot_omega()
        self.plot_gamma()
        self.add_omega_and_gamma_titles()
        self.save_omega_and_gamma_plot(format_type)

    def plot_omega(self):
        omega_plot = PlotGreek(self, self.axis_omega)
        omega_plot.plot_greek(self.trial.data_set.omega_path)
        omega_plot.add_axis_labels("Omega")

    def plot_gamma(self):
        gamma_plot = PlotGreek(self, self.axis_gamma)
        gamma_plot.plot_greek(self.trial.data_set.gamma_path)
        gamma_plot.add_axis_labels("Gamma")

    def add_omega_and_gamma_titles(self):
        plot_title = self.get_omega_and_gamma_plot_title()
        self.greek_fig.suptitle(plot_title)
        #self.axis_omega.set_title("Omega")
        #self.axis_gamma.set_title("Gamma")

    def get_omega_and_gamma_plot_title(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        plot_title = f"{data_set}, {power_string} dBm, Trial {trial_number}"
        return plot_title

    def save_omega_and_gamma_plot(self, format_type):
        plot_file_name = self.get_omega_and_gamma_file_name()
        plot_path = os.path.join(self.trial.data_set.omega_and_gamma_path, plot_file_name)
        plt.tight_layout()
        plt.savefig(plot_path, bbox_inches='tight', format=format_type)

    def get_omega_and_gamma_file_name(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        plot_file_name = f"Omega_and_Gamma_{data_set}_{power_string}_dBm_Trial_{trial_number}"
        return plot_file_name

    def create_trial_plots(self, plot_name):
        {"Detuning vs time": self.plot_detuning_vs_time,
         "Frequency of peak": self.plot_frequency_of_peak,
         "Transmission peak": self.plot_transmission_peak,
         "Colour plots": self.plot_colour_plots}[plot_name]()

    def plot_detuning_vs_time(self):
        detunings, timestamps = self.get_detunings_and_timestamps()
        plt.plot(timestamps, detunings)
        self.add_detuning_vs_time_labels()
        plt.show()

    def get_detunings_and_timestamps(self):
        detuning_time_data = [(detuning_obj.detuning, detuning_obj.timestamp)
                              for detuning_obj in self.trial.detuning_objects]
        detunings, timestamps = zip(*detuning_time_data)
        return detunings, timestamps

    def add_detuning_vs_time_labels(self):
        plt.xlabel("Timestamp (s)")
        plt.ylabel("Detuning (Hz)")
        plt.title(f"Detuning vs Time for {self.power_obj.folder_name}")

    def plot_frequency_of_peak(self):
        peak_frequencies = [spectrum_obj.S21_centre_frequency
                            for detuning_obj in self.trial.detuning_objects
                            for spectrum_obj in detuning_obj.spectrum_objects]
        plt.plot(peak_frequencies)
        self.add_frequency_of_peak_labels()
        plt.show()

    def add_frequency_of_peak_labels(self):
        plt.xlabel("Spectrum number")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Peak Frequency vs Spectrum Number\n"
                   f"for {self.power_obj.folder_name}"))

    def plot_transmission_peak(self):
        timestamps, transmission_peaks = self.get_transmission_peaks()
        plt.plot(timestamps, transmission_peaks, '.-')
        self.add_transmission_peak_labels()
        plt.show()

    def get_transmission_peaks(self):
        transmission_data = [(detuning_obj.timestamp,
                              detuning_obj.transmission.S21_centre_frequency)
                             for detuning_obj in self.trial.detuning_objects]
        timestamps, transmission_peaks = zip(*transmission_data)
        return timestamps, transmission_peaks

    def add_transmission_peak_labels(self):
        plt.xlabel("Timestamp (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Peak Frequency of Transmission\n"
                   f"vs Time for {self.power_obj.folder_name}, Trial {self.trial_number}"))

    def plot_colour_plots(self):
        for i in self.trial.detuning_objects:
            print(len(i.S21), len(i.frequency))

    def create_detuning_plots(self, plot_name):
        for detuning_obj in self.trial.detuning_objects:
            detuning_plot_obj = DetuningPLot(detuning_obj)
            detuning_plot_obj.create_detuning_plots(plot_name)
