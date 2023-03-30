import math

class PlotShape():

    def __init__(self, count, aspect_ratio):
        self.count = count
        self.aspect_ratio = aspect_ratio
        self.set_grid_size()

    def set_grid_size(self):
        self.set_row_and_column_sizes()
        self.set_row_column_pairs()
        self.select_row_column_pair()
        self.dimensions = [self.rows, self.columns]

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
