from DataSet import DataSet

my_data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
my_data_set.plot_spectra(markers=True, fit=True, save=True)
my_data_set.envelope_vertices(save=True)
my_data_set.peak_fits(save=True)
