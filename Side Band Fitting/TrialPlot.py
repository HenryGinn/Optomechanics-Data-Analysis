from DetuningPlot import DetuningPlot

class TrialPlot():

    def __init__(self, trial_obj):
        self.trial = trial_obj

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
        peak_frequencies = self.get_peak_frequencies()
        plt.plot(peak_frequencies)
        self.add_frequency_of_peak_labels()
        plt.show()

    def get_peak_frequencies(self):
        peak_frequencies = [spectrum_obj.S21_centre_frequency
                            for detuning_obj in self.trial.detuning_objects
                            for spectrum_obj in detuning_obj.spectrum_objects]
        return peak_frequencies

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
