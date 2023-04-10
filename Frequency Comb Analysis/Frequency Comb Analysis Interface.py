from DataSet import DataSet

data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
#data_set.plot_spectra(markers=True, fit=True, noise=True, subplots=None, layout="Constrained")
#data_set.envelope_vertices(save=True, layout="Adjust")
#data_set.peak_fits(layout="Adjust")
#data_set.peak_gaps(layout="Adjust")
#data_set.peak_count(layout="Adjust")
#data_set.raw_data_peaks("Save")
data_set.reverse_fourier_transform("Save")
data_set.reverse_fourier_transform("Plot", universal_legend=True)
