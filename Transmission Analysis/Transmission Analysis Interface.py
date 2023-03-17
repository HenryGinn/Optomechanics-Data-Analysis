from DataSet import DataSet

my_data_set = DataSet("14112022", 2)
my_data_set.read_raw_transmission()
my_data_set.plot_transmission("Raw", subplots=4)
#my_data_set.align_transmission(group_size=3)
#my_data_set.plot_transmission("Aligned", subplots=5)
