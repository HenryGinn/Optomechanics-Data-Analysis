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
my_data_set = DataSet("16112022_overnight", folder_structure_type=2)
#my_data_set = DataSet("19112022", folder_structure_type=3)
#my_data_set = DataSet("21112022", folder_structure_type=3)
#my_data_set = DataSet("22112022", folder_structure_type=3)

my_data_set.process_folders()
my_data_set.process_transmission()
#my_data_set.process_spectrum()
#my_data_set.create_omega_objects()
#my_data_set.create_gamma_objects()
#my_data_set.process_omega()
#my_data_set.average_omega()
#my_data_set.process_gamma()
#my_data_set.average_gamma()
#my_data_set.create_trial_plots("Transmission peak")
#my_data_set.create_detuning_plots("Frequency of peak")
#my_data_set.plot_omega("pdf")
#my_data_set.plot_gamma("pdf")
#my_data_set.plot_omega_and_gamma()
