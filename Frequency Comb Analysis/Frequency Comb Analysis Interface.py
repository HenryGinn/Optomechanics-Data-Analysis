from DataSet import DataSet

data_set = DataSet("06122022_overnight", drifts=None, detunings=None)
#data_set.plot_spectra(markers=True, fit=True, noise=True, subplots=None, layout="Constrained", save=True, show=True)
#data_set.envelope_vertices(save=True, layout="Adjust")
#data_set.peak_fits(layout="Adjust")
data_set.spectra_peak()
