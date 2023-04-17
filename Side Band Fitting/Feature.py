import os

from Utils import make_folder

class Feature():

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj
        self.loaded = False

    def set_commands(self):
        self.commands = {"Save": self.save_data,
                         "Load": self.load_data,
                         "Plot": self.create_plot}

    def execute(self, command, **kwargs):
        function = self.commands[command]
        function(**kwargs)
    
    def set_folder_path(self):
        self.folder_path = os.path.join(self.data_set_obj.results_path, self.name)
        make_folder(self.folder_path, message=True)

    def save_data(self):
        self.set_paths()
        self.load_necessary_data_for_saving()
        print(f"Saving '{self.name}' data")
        self.save_data_set_obj(self.data_set_obj)
        self.loaded = True

    def load_necessary_data_for_saving(self):
        pass

    def load_data(self):
        self.set_paths()
        if not self.data_is_saved():
            self.execute("Save")
        elif not self.loaded:
            print(f"Loading '{self.name}' data")
            self.do_load_data()
        self.loaded = True
    
    def ensure_data_is_loaded(self):
        if not self.loaded:
            self.execute("Load")

    def create_plot(self, **kwargs):
        if hasattr(self, "create_plots"):
            self.execute("Load")
            self.plot(**kwargs)
        else:
            print("Sorry, this feature does not have a 'plot' method implemented")

    def plot(self, **kwargs):
        self.process_args(**kwargs)
        lines_objects = self.get_lines_objects()
        title = f"{self.data_set_obj} {self.name}"
        self.create_plots(lines_objects, title, kwargs)

    def process_args(self, **kwargs):
        self.process_subplots(**kwargs)
        self.process_aspect_ratio(**kwargs)

    def process_subplots(self, **kwargs):
        if "subplots" in kwargs:
            self.subplots = kwargs["subplots"]
        else:
            self.subplots = None

    def process_aspect_ratio(self, **kwargs):
        if "aspect_ratio" in kwargs:
            self.aspect_ratio = kwargs["aspect_ratio"]
        else:
            self.aspect_ratio = None

    def create_plot_new(self):
        self.execute("Save")
        self.execute("Plot")
