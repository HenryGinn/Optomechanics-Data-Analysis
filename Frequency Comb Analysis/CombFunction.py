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

    def ensure_data_is_loaded(self):
        if not self.loaded:
            self.execute("Load")

