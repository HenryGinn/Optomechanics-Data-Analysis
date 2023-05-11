import os

from DataSet import DataSet

"""
Before using the program, there are several things you need to check
1: What is the folder structure?
2: Are the folder and file names what the program is expecting?
3: Is your repository saved in the correct place relative to the
   data set?

Details about how to check all of these are given in the README.

Options for creating plots by trial are "Detuning vs time", "Frequency
of peak", "Transmission peak", and "Colour plots". Options for creating
plots by detuning are "Frequency of peak"
"""

def get_data_set(data_set_data):
    name, structure = data_set_data
    data_set = DataSet(name,
                       folder_structure_type=structure,
                       data_set_path=data_set_path)
    return data_set

def process_data_set(data_set):
    #data_set.transmission_fit("Plot", subplots=20, aspect_ratio=1.7)
    #data_set.spectra_valid("Save")
    #data_set.spectra_valid("Plot", subplots=None)
    #data_set.spectra_fit("Plot", subplots=1, width=None)
    #data_set.fit_heuristic("Save")
    #data_set.fit_heuristic("Plot", subplots=20)
    #data_set.spectra_fit_filtered("Save")
    #data_set.spectra_fit_filtered("Plot", subplots=20)
    #data_set.greek("Plot")
    data_set.fit_properties_filter("Save")
    #data_set.fit_properties_filter("Plot")
    data_set.fit_properties_filter("Save")
    data_set.fit_properties_filter("Plot")
    #data_set.average_greek("Plot")
    
def process_all_data_sets():
    for data_set_data in data_sets:
        data_set = get_data_set(data_set_data)
        print(f"\nProcessing {data_set.folder_name}")
        process_data_set(data_set)

data_sets = [("15112022", 1),
             ("16112022_overnight", 2),
             ("17112022", 2),
             ("18112022", 2),
             ("19112022", 3),
             ("21112022", 3),
             ("22112022", 3)]

if os.name == "nt":
    data_set_path = "D:\\Documents\\Experiments\\RT_exp4"
else:
    data_set_path=None

data_set_data = data_sets[1]
data_set = get_data_set(data_set_data)
process_data_set(data_set)
#process_all_data_sets()
