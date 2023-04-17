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
    data_set.spectra("Load")
    
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

data_set_path = "D:\\Documents\\Experiments\\RT_exp4"

data_set_data = data_sets[0]
data_set = get_data_set(data_set_data)
process_data_set(data_set)
#process_all_data_sets()
