import math

import matplotlib.pyplot as plt

class Plot():

    aspect_ratio = 16/9

    def __init__(self, line_objects):
        self.line_objects = line_objects
        self.count = len(line_objects)
        self.set_grid_size()

    def set_grid_size(self):
        self.set_row_and_column_sizes()
        self.set_row_column_pairs()
        self.select_row_column_pair()

    def set_row_and_column_sizes(self):
        self.set_row_sizes()
        self.set_column_sizes()

    def set_row_sizes(self):
        row_size = math.sqrt(self.count / self.aspect_ratio)
        self.row_small = math.floor(row_size)
        self.row_large = math.ceil(row_size)

    def set_column_sizes(self):
        column_size = math.sqrt(self.count * self.aspect_ratio)
        self.column_small = math.floor(column_size)
        self.column_large = math.ceil(column_size)

    def set_row_column_pairs(self):
        self.row_column_pairs = {(self.row_small, self.column_small): {},
                                 (self.row_small, self.column_large): {},
                                 (self.row_large, self.column_small): {},
                                 (self.row_large, self.column_large): {}}
        self.populate_row_column_pairs()

    def populate_row_column_pairs(self):
        for pair in self.row_column_pairs.keys():
            self.row_column_pairs[pair] = self.get_row_column_pair_data(pair)

    def get_row_column_pair_data(self, pair):
        size = pair[0] * pair[1]
        aspect_ratio = pair[1] / pair[0]
        pair_data_dict = {"Size": size, "Aspect Ratio": aspect_ratio}
        return pair_data_dict

    def select_row_column_pair(self):
        big_enough_pairs = {pair: pair_data for pair, pair_data in self.row_column_pairs.items()
                            if pair_data["Size"] >= self.count}
        aspect_ratio_dict = {pair_data["Aspect Ratio"]: pair
                             for pair, pair_data in big_enough_pairs.items()}
        best_pair = max(aspect_ratio_dict.items(), key=self.get_aspect_ratio_score)
        self.rows, self.columns = best_pair[1]

    def get_aspect_ratio_score(self, aspect_ratio_key_value):
        aspect_ratio = aspect_ratio_key_value[0]
        score = max(aspect_ratio/self.aspect_ratio, self.aspect_ratio/aspect_ratio)
        return score

    def create_figure(self):
        fig, axes = plt.subplots(nrows=self.rows, ncols=self.columns)
        self.plot_lines(axes)
        #self.suptitle("My Title")
        self.show_plot(fig)

    def plot_lines(self, axes):
        for ax, line_obj in zip(axes.flatten(), self.line_objects):
            self.plot_line_obj(ax, line_obj)

    def plot_line_obj(self, ax, line_obj):
        ax.plot(line_obj.x_values, line_obj.y_values)
        ax.set_title(line_obj.title)

    def show_plot(self, fig):
        fig.tight_layout()
        plt.show()
        plt.close()
