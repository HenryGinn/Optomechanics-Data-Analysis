import numpy as np

from Feature import Feature
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line

class PlotSpectra(Feature):

    name = "Plot Spectra"
    y_threshold = 6*10**-15

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()

    def process_kwargs(self, **kwargs):
        self.kwargs = kwargs
        self.process_average_size_kwarg()

    def process_average_size_kwarg(self):
        if "average" in self.kwargs:
            self.average_size = self.kwargs["average"]
        else:
            self.average_size = None

    def set_paths(self):
        self.set_folder_path()

    def save_data(self):
        pass

    def do_load_data(self):
        self.data_set_obj.average_spectra("Load", average=self.average_size)

    def create_plots(self, title, **kwargs):
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                for detuning_obj in trial_obj.detuning_objects:
                    self.create_detuning_plot(detuning_obj, kwargs)

    def create_detuning_plot(self, detuning_obj, kwargs):
        lines_objects = self.get_lines_objects(detuning_obj)
        plots_obj = Plots(lines_objects, kwargs)
        plots_obj.parent_results_path = self.folder_path
        plots_obj.title = f"{detuning_obj}\n "
        plots_obj.plot()

    def get_lines_objects(self, detuning_obj):
        lines_objects = [self.get_lines_obj(detuning_obj, average_spectrum_obj)
                         for average_spectrum_obj in detuning_obj.average_spectrum_objects]
        return lines_objects

    def get_lines_obj(self, detuning_obj, average_spectrum_obj):
        line_objects = self.get_line_objects(detuning_obj, average_spectrum_obj)
        lines_obj = Lines(line_objects)
        self.process_lines_obj(lines_obj, average_spectrum_obj)
        self.add_average_line(lines_obj, average_spectrum_obj)
        return lines_obj

    def get_line_objects(self, detuning_obj, average_spectrum_obj):
        indices = average_spectrum_obj.spectrum_indices
        spectrum_objects = np.array(detuning_obj.spectrum_objects)[indices]
        line_objects = [self.get_line_obj(spectrum_obj)
                        for spectrum_obj in spectrum_objects]
        return line_objects

    def get_line_obj(self, spectrum_obj):
        spectrum_obj.load_S21()
        x_values = spectrum_obj.frequency
        y_values = spectrum_obj.S21
        x_values = x_values[y_values > self.y_threshold]
        y_values = y_values[y_values > self.y_threshold]
        line_obj = Line(x_values, y_values, marker=".", linewidth=0)
        return line_obj

    def process_lines_obj(self, lines_obj, average_spectrum_obj):
        lines_obj.set_rainbow_lines()
        lines_obj.title = f"Group {average_spectrum_obj.group_index}"

    def add_average_line(self, lines_obj, average_spectrum_obj):
        x_values = average_spectrum_obj.frequency + average_spectrum_obj.frequency_shift
        y_values = average_spectrum_obj.S21
        x_values = x_values[y_values > self.y_threshold]
        y_values = y_values[y_values > self.y_threshold]
        line_obj = Line(x_values, y_values,
                        colour="k", linewidth=3, marker=".")
        lines_obj.line_objects.append(line_obj)
