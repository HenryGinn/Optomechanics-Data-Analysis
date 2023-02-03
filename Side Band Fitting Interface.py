from DataSet import DataSet

my_data_set = DataSet("15112022", folder_structure_type=1)
#my_data_set = DataSet("16112022_overnight", folder_structure_type=2)

#my_data_set.output_power_folder_names()
#my_data_set.output_transmission_folder_paths()
#my_data_set.output_spectrum_folder_paths()

my_data_set.process_power_folders()
