from Transmission import Transmission

class AlignedTransmission(Transmission):

    def __init__(self, transmission_objects):
        self.transmission_objects = transmission_objects
        self.frequency = transmission_objects[0].frequency

    def align_transmissions(self):
        self.set_peak_indexes()
        self.set_max_and_min_peak_indexes()
        self.offset_S21()
        self.offset_frequency()

    def set_peak_indexes(self):
        self.peak_indexes = [transmission_obj.peak_index
                             for transmission_obj in self.transmission_objects]

    def set_max_and_min_peak_indexes(self):
        self.max_peak_index = max(self.peak_indexes)
        self.min_peak_index = min(self.peak_indexes)

    def offset_S21(self):
        for transmission_obj in self.transmission_objects:
            self.set_S21_offset(transmission_obj)

    def set_S21_offset(self, transmission_obj):
        left_index = transmission_obj.peak_index - self.min_peak_index
        right_index = len(transmission_obj.S21) - (self.max_peak_index - transmission_obj.peak_index)
        transmission_obj.S21_offset = transmission_obj.S21[left_index:right_index]

    def offset_frequency(self):
        cutoff_size = self.max_peak_index - self.min_peak_index
        frequency_offset_length = len(self.frequency) - cutoff_size
        self.frequency = self.frequency[:frequency_offset_length]
        self.frequency_shift = self.frequency[self.min_peak_index]
        self.frequency -= self.frequency_shift
