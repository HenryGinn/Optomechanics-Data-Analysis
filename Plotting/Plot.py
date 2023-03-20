import math

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class Plot():

    """
    An instance of Plot will be a single figure.
    This figure can have multiple subplots, and corresponding to
    each subplot is a Lines object. A Lines object has a collection
    of Line objects associated with it.
    """

    aspect_ratio = 2/3

    def __init__(self, plots_obj, lines_objects, plot_index):
        self.plots_obj = plots_obj
        self.lines_objects = lines_objects[0]
        self.plot_index = plot_index
        self.count = len(self.lines_objects)
        self.set_grid_size()

    def set_grid_size(self):
        self.set_row_and_column_sizes()
        self.set_row_column_pairs()
        self.select_row_column_pair()

    def set_row_and_column_sizes(self):
        self.set_row_sizes()
        self.set_column_sizes()

    def set_row_sizes(self):
        row_size = math.sqrt(self.count * self.aspect_ratio)
        self.row_small = math.floor(row_size)
        self.row_large = math.ceil(row_size)

    def set_column_sizes(self):
        column_size = math.sqrt(self.count / self.aspect_ratio)
        self.column_small = math.floor(column_size)
        self.column_large = math.ceil(column_size)

    def set_row_column_pairs(self):
        self.set_pairs()
        self.row_column_pairs = {pair: {} for pair in self.pairs}
        self.populate_row_column_pairs()

    def set_pairs(self):
        self.pairs = [(self.row_small, self.column_small),
                      (self.row_small, self.column_large),
                      (self.row_large, self.column_small),
                      (self.row_large, self.column_large)]

    def populate_row_column_pairs(self):
        for pair in self.row_column_pairs.keys():
            self.row_column_pairs[pair] = self.get_row_column_pair_data(pair)

    def get_row_column_pair_data(self, pair):
        size = pair[0] * pair[1]
        aspect_ratio = self.get_aspect_ratio(pair)
        pair_data_dict = {"Size": size, "Aspect Ratio": aspect_ratio}
        return pair_data_dict

    def get_aspect_ratio(self, pair):
        if pair[0] != 0 and pair[1] != 0:
            aspect_ratio = pair[0] / pair[1]
        else:
            aspect_ratio = None
        return aspect_ratio

    def select_row_column_pair(self):
        if len(self.row_column_pairs) == 1:
            self.exact_ratio_pair()
        else:
            self.non_exact_ratio_pairs()

    def exact_ratio_pair(self):
        self.rows, self.columns = self.pairs[0]

    def non_exact_ratio_pairs(self):
        is_grid_big_enough = self.get_is_grid_big_enough()
        row_column_pair_functions = self.get_row_column_pair_functions()
        row_column_pair_function, *args = row_column_pair_functions[is_grid_big_enough]
        row_column_pair_function(*args)
        self.rows, self.columns = self.best_pair

    def get_is_grid_big_enough(self):
        is_grid_big_enough = tuple([row_column_pair["Size"] >= self.count
                                    for row_column_pair in self.row_column_pairs.values()])
        return is_grid_big_enough

    def get_row_column_pair_functions(self):
        row_column_pair_functions = {(True, True, True, True): (self.set_best_pair, 0),
                                     (False, True, True, True): (self.middle_pair_compare,),
                                     (False, True, False, True): (self.set_best_pair, 1),
                                     (False, False, True, True): (self.set_best_pair, 2),
                                     (False, False, False, True): (self.set_best_pair, 3)}
        return row_column_pair_functions

    def set_best_pair(self, pair_index):
        self.best_pair = self.pairs[pair_index]

    def middle_pair_compare(self):
        self.set_aspect_ratio_scores()
        self.compare_aspect_ratio_scores()

    def set_aspect_ratio_scores(self):
        aspect_ratio_1 = self.row_column_pairs[self.pairs[1]]["Aspect Ratio"]
        aspect_ratio_2 = self.row_column_pairs[self.pairs[2]]["Aspect Ratio"]
        self.aspect_ratio_score_1 = self.get_aspect_ratio_score(aspect_ratio_1)
        self.aspect_ratio_score_2 = self.get_aspect_ratio_score(aspect_ratio_2)

    def get_aspect_ratio_score(self, aspect_ratio):
        if aspect_ratio is not None:
            score = max(aspect_ratio / self.aspect_ratio,
                        self.aspect_ratio / aspect_ratio)
        else:
            score = None
        return score

    def compare_aspect_ratio_scores(self):
        if self.aspect_ratio_score_1 < self.aspect_ratio_score_2:
            self.set_best_pair(1)
        else:
            self.set_best_pair(2)

    def create_figure(self):
        fig, axes = plt.subplots(nrows=self.rows, ncols=self.columns)
        self.plot_axes(axes)
        fig.suptitle(f"{self.plots_obj.title}, Figure {self.plot_index}")
        self.show_plot(fig)

    def plot_axes(self, axes):
        axes_flat = self.get_axes_flat(axes)
        for ax, lines_obj in zip(axes_flat, self.lines_objects):
            self.plot_lines(ax, lines_obj)
            self.set_labels(ax, lines_obj)

    def plot_lines(self, ax, lines_obj):
        for line_obj in lines_obj.line_objects:
            ax.plot(line_obj.x_values, line_obj.y_values)

    def set_labels(self, ax, lines_obj):
            ax.set_title(lines_obj.title)
            ax.set_xlabel(lines_obj.x_label)
            ax.set_ylabel(lines_obj.y_label)

    def get_axes_flat(self, axes):
        if isinstance(axes, np.ndarray):
            axes_flat = axes.flatten()
        else:
            axes_flat = [axes]
        return axes_flat

    def show_plot(self, fig):
        fig.tight_layout()
        plt.show()
        plt.close()
