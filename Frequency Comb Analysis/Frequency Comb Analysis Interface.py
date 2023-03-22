from DataSet import DataSet

#script_path = "/home/henry/Documents/Physics Internship/Optomechanics-Data-Analysis/Frequency Comb Analysis"

my_data_set = DataSet("06122022_overnight", drifts=-1, detunings=-1)
#my_data_set.set_aligned_spectra()
my_data_set.load_aligned_spectra()
#my_data_set.set_peak_coordinates()
my_data_set.load_peak_coordinates()
my_data_set.fit_peaks()
my_data_set.plot_spectra(groups=-1, markers=True, fit=True)
