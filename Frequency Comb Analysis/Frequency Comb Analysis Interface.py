from DataSet import DataSet

#script_path = "/home/henry/Documents/Physics Internship/Optomechanics-Data-Analysis/Frequency Comb Analysis"

my_data_set = DataSet("06122022_overnight")
my_data_set.process_spectrum()
my_data_set.plot_spectra()
