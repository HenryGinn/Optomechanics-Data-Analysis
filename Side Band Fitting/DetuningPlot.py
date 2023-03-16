import matplotlib.pyplot as plt

class DetuningPlot():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj

    def plot_peak_S21_drift(self):
        plt.plot(self.frequency[np.array(self.detuning.spectrum_centre_indexes)])
        plt.xlabel("Spectrum number")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Frequency of Peak S21 vs Spectrum\n"
                   f"Number at {self.trial.power_obj.power_string} dBm"))
        plt.show()
    
    def plot_frequency_of_peak(self):
        peak_frequencies = [spectrum_obj.S21_centre_frequency
                            for spectrum_obj in self.detuning.spectrum_objects]
        plt.plot(peak_frequencies)
        self.add_frequency_of_peak_labels()
        plt.show()

    def add_frequency_of_peak_labels(self):
        plt.xlabel("Spectrum number")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Peak Frequency vs Spectrum Number\n"
                   f"for {self.detuning.trial.power_obj.folder_name}, {self.detuning.detuning} Hz"))
