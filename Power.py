from Trial import Trial

class Power():

    """
    This class handles all the data for a specific power within one dataset.
    Organising the processing of the trials and plotting things happens here.
    """
    
    def __init__(self, data_set, power_folder, transmission_path, spectrum_path):
        self.data_set = data_set
        self.folder_name = power_folder
        self.transmission_path = transmission_path
        self.spectrum_path = spectrum_path
        self.power = self.get_power_from_folder_name()

    def get_power_from_folder_name(self):
        try:
            power = self.folder_name[0:2]
            power = round(float(power), 1)
        except:
            raise Exception(f"Power could not be read from folder name: {folder_name}")
        return power

    def process_power(self):
        self.set_trial_paths()
        self.set_trial_list()

    def set_trial_paths(self):
        set_trial_path_functions = {1: self.set_trial_paths_A,
                                    2: self.set_trial_paths_A,
                                    3: self.set_trial_paths_B}
        set_trial_path_functions[self.data_set.folder_structure_type]()

    def set_trial_paths_A(self):
        self.trial_paths_spectrum = [self.spectrum_path]
        self.trial_paths_transmission = [self.transmission_path]

    def set_trial_paths_B(self):
        for folder_name in self.spectrum_path:
            print(folder_name)

    def set_trial_list(self):
        self.trial_list = []

    def __str__(self):
        string = (f"Data set: {self.data_set}\n"
                  f"Folder name: {self.folder_name}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n"
                  f"Power: {self.power}")
        return string
