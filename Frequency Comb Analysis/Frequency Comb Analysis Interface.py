from DataSet import DataSet

#script_path = "/home/henry/Documents/Physics Internship/Optomechanics-Data-Analysis/Frequency Comb Analysis"

my_data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
my_data_set.plot_spectra(subplots=2, noise=True, markers=True, fit=False)
#my_data_set.plot_peak_fits()
#my_data_set.envelope_trends("Plot")
#my_data_set.peak_gaps()
