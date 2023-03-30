from DataSet import DataSet

my_data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
#my_data_set.plot_spectra(noise=True, markers=True, fit=True)
my_data_set.peak_fits()
#my_data_set.peak_gaps()
