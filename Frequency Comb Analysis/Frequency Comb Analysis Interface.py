from DataSet import DataSet

#script_path = "/home/henry/Documents/Physics Internship/Optomechanics-Data-Analysis/Frequency Comb Analysis"

my_data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
#my_data_set.set_aligned_spectra()
my_data_set.load_aligned_spectra()
my_data_set.save_noise_threshold()
#my_data_set.load_noise_threshold()
my_data_set.set_peak_coordinates()
#my_data_set.load_peak_coordinates()
#my_data_set.save_fit_peaks()
#my_data_set.plot_spectra(groups=0, noise=True, markers=True)#, fit=True)
