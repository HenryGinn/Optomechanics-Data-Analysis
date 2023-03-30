from DataSet import DataSet

my_data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
#my_data_set.plot_spectra(markers=True, fit=True, adjust=True)
#my_data_set.envelope_vertices()
my_data_set.peak_fits(aspect_ratio=2, adjust=True)
