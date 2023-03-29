from DataSet import DataSet

#script_path = "/home/henry/Documents/Physics Internship/Optomechanics-Data-Analysis/Frequency Comb Analysis"

my_data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
my_data_set.peak_fits()
#my_data_set.plot_spectra(groups=0, noise=False, markers=False, fit=True)
#my_data_set.plot_peak_fits(groups=3)
#my_data_set.envelope_trends("Plot")
#my_data_set.peak_gaps()
