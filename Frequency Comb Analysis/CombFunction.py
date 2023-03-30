import os

from Utils import make_folder

class CombFunction():

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj
        self.loaded = False

    def set_commands(self):
        self.commands = {"Save": self.save_data,
                         "Load": self.load_data,
                         "Plot": self.create_plot}

    def execute(self, command, *args):
        function = self.commands[command]
        function(*args)
    
    def set_folder_path(self):
        self.folder_path = os.path.join(self.data_set_obj.results_path, self.name)
        make_folder(self.folder_path, message=True)

    def save_data(self):
        self.set_paths()
        self.load_necessary_data_for_saving()
        print(f"Saving '{self.name}' Data")
        self.save_data_set_obj(self.data_set_obj)
        self.loaded = True

    def load_necessary_data_for_saving(self):
        pass

    def load_data(self):
        self.set_paths()
        if not self.data_is_saved():
            self.execute("Save")
        elif not self.loaded:
            print(f"Loading '{self.name}' Data")
            self.do_load_data()
        self.loaded = True
    
    def ensure_data_is_loaded(self):
        if not self.loaded:
            self.execute("Load")

    def create_plot(self):
        if hasattr(self, "plot"):
            self.execute("Load")
            self.plot()
        else:
            print("Sorry, this feature does not have a 'plot' method implemented")
