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

#my_data_set = DataSet("15112022", folder_structure_type=1)
#my_data_set = DataSet("16112022_overnight", folder_structure_type=2)
#my_data_set = DataSet("17112022", folder_structure_type=2)
my_data_set = DataSet("18112022", folder_structure_type=2)
#my_data_set = DataSet("19112022", folder_structure_type=3)
#my_data_set = DataSet("21112022", folder_structure_type=3)
#my_data_set = DataSet("22112022", folder_structure_type=3)

my_data_set.process_folders()

#my_data_set.process_transmission()
my_data_set.process_spectrum()

my_data_set.create_greek_objects()
my_data_set.process_greek(6)
my_data_set.average_greek()
#my_data_set.plot_greek()

#my_data_set.omega_power_drift(False)

#my_data_set.create_trial_plot_objects()
#my_data_set.create_trial_plots("Transmission peak")
#my_data_set.create_detuning_plots("Frequency of peak")
