from DataSet import DataSet

"""
Before using the program, there are several things you need to check
1: What is the folder structure? Details on this are found in DataSet
2: Are the folder and file names what the program is expecting?
   If there is a program that contains a data set with the same
   structure as yours that is intended to fix names, you should
   check that file for any notes,
   The main cause of error are numberings such as 0, 1, ..., 10, 11.
   When sorting as a string this will get 0, 10, 1, 11, so numbers
   should be padded with leading 0s: 00, 01, ..., 10, 11.
3: Is your repository saved in the correct place relative to the
   data set? Details about this are given in Side Band Docs.
"""

#my_data_set = DataSet("15112022", folder_structure_type=1)
#my_data_set = DataSet("16112022_overnight", folder_structure_type=2)
my_data_set = DataSet("19112022", folder_structure_type=3)

#my_data_set.output_power_folder_names()
#my_data_set.output_transmission_folder_paths()
#my_data_set.output_spectrum_folder_paths()

my_data_set.process_power_folders()
