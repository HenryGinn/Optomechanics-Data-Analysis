from CombFunction import CombFunction

class PeakGaps(CombFunction):

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def save_data(self):
        self.set_paths()

    def set_paths(self):
        self.path = None

    def load_data(self):
        self.ensure_data_file_exists()

    def ensure_data_file_exists(self):
        self.set_paths()
        if not os.path.exists(self.path):
            self.execute("Save")

    def create_plot(self):
        self.ensure_loaded()
