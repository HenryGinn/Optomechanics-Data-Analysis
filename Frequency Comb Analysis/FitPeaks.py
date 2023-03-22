import numpy as np

from PeakLine import PeakLine

class FitPeaks():

    def __init__(self, group_obj):
        self.group_obj = group_obj
        self.spectrum_obj = self.group_obj.spectrum_obj
        self.set_peak_data()
        self.set_peak_line_objects()

    def set_peak_data(self):
        self.peak_indices = self.spectrum_obj.peak_indices
        self.peak_frequencies = self.spectrum_obj.peak_frequencies
        self.peak_S21s = self.spectrum_obj.peak_S21s
        self.peak_S21s_log = np.log(self.peak_S21s)

    def set_peak_line_objects(self):
        self.centre_peak_index = np.argmax(self.peak_S21s)
        self.set_peak_line_left()
        self.set_peak_line_right()
        self.peak_lines = [self.peak_line_left, self.peak_line_right]

    def set_peak_line_left(self):
        x_values = self.peak_frequencies[:self.centre_peak_index + 1]
        y_values = self.peak_S21s_log[:self.centre_peak_index + 1]
        self.peak_line_left = PeakLine(self, x_values, y_values, "Left")

    def set_peak_line_right(self):
        x_values = self.peak_frequencies[self.centre_peak_index:]
        y_values = self.peak_S21s_log[self.centre_peak_index:]
        self.peak_line_right = PeakLine(self, x_values, y_values, "Right")

    def fit_peaks(self):
        for peak_line in self.peak_lines:
            peak_line.fit_line()
            peak_line.set_values_fit()
