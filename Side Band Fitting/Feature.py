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
        self.process_kwargs(**kwargs)
        function(**kwargs)

    def process_kwargs(self, **kwargs):
        pass
    
    def set_folder_path(self):
        self.folder_path = os.path.join(self.data_set_obj.results_path, self.name)
        make_folder(self.folder_path, message=True)

    def save_data(self, **kwargs):
        self.set_paths()
        self.load_necessary_data_for_saving()
        print(f"Saving '{self.name}' data")
        self.save_data_set_obj(self.data_set_obj)
        self.loaded = True

    def load_necessary_data_for_saving(self):
        pass

    def load_data(self, **kwargs):
        self.set_paths()
        self.process_load_data(**kwargs)
        self.loaded = True

    def process_load_data(self, **kwargs):
        if not self.data_is_saved():
            self.execute("Save", **kwargs)
        elif not self.loaded:
            print(f"Loading '{self.name}' data")
            self.do_load_data()

    def data_is_saved(self):
        return True
    
    def ensure_data_is_loaded(self):
        if not self.loaded:
            self.execute("Load")

    def load_necessary_data_for_plotting(self):
        pass

    def create_plot(self, **kwargs):
        if hasattr(self, "create_plots"):
            self.execute("Load", **kwargs)
            self.load_necessary_data_for_plotting()
            self.create_plots(**kwargs)
        else:
            print("Sorry, this feature does not have a 'create_plots' method implemented")

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
