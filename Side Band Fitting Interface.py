from DataSet import DataSet

"""
Before using the program, there are several things you need to check
1: What is the folder structure?
2: Are the folder and file names what the program is expecting?
3: Is your repository saved in the correct place relative to the
   data set?

Details about how to check all of these are given in the README.
"""

#my_data_set = DataSet("15112022", folder_structure_type=1)
my_data_set = DataSet("16112022_overnight", folder_structure_type=2)
#my_data_set = DataSet("19112022", folder_structure_type=3)

my_data_set.process_folder_structure()
my_data_set.process_transmission()
#my_data_set.process_S21()
#my_data_set.process_gamma()
#my_data_set.save_gamma()
my_data_set.create_trend_plots()
