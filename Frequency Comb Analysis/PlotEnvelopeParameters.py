from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line

class PlotEnvelopeParameters():

    name = "Envelope Parameters"

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj

    def plot(self, legend):
        self.legend = legend
        self.load_data()
        self.plot_data_set()

    def load_data(self):
        self.data_set_obj.peak_fits("Load")

    def plot_data_set(self):
        lines_objects = self.get_lines_objects()
        title = f"{self.data_set_obj} {self.name}"
        self.create_plots(lines_objects, title)

    def get_lines_objects(self):
        lines_obj_gradient = self.get_lines_obj_gradient()
        lines_obj_intercept = self.get_lines_obj_intercept()
        lines_objects = [lines_obj_gradient, lines_obj_intercept]
        return lines_objects

    def get_lines_obj_gradient(self):
        line_objects = [self.get_line_objects_gradient(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj_gradient = Lines(line_objects, legend=self.legend)
        return lines_obj_gradient

    def get_line_objects_gradient(self, drift_obj):
        label = drift_obj.drift_value
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = [detuning_obj.fitting_parameters[0] for detuning_obj in drift_obj.detuning_objects]
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def get_lines_obj_intercept(self):
        line_objects = [self.get_line_objects_intercept(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj_intercept = Lines(line_objects, legend=self.legend)
        return lines_obj_intercept

    def get_line_objects_intercept(self, drift_obj):
        label = drift_obj.drift_value
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = [detuning_obj.fitting_parameters[1] for detuning_obj in drift_obj.detuning_objects]
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def create_plots(self, lines_objects, title):
        plot_obj = Plots(lines_objects)
        plot_obj.title = title
        plot_obj.plot()
