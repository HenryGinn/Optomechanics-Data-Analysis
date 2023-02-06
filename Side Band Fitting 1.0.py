import os
import sys
from scipy import optimize
from scipy.optimize import leastsq
from numpy import *
import glob
from matplotlib import *
from pylab import *
import math
import numpy as np

import matplotlib.font_manager as fm
font_names = [f.name for f in fm.fontManager.ttflist]
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

############################### FILE HANDLING ###############################

def get_file_detuning_1(file):
    underscore_locations = [index for index, character in enumerate(file)
                            if character == "_"]
    left = underscore_locations[9] + 1
    right = underscore_locations[10]
    detuning = file[left:right]
    detuning = int(float(detuning))
    return detuning

def get_file_detuning_2(file):
    underscore_locations = [index for index, character in enumerate(file)
                            if character == "_"]
    left = underscore_locations[10] + 1
    right = underscore_locations[11]
    detuning = file[left:right]
    detuning = int(float(detuning))
    return detuning

def get_files_1(data_set, power_folder):
    parent_folder = os.path.dirname(os.path.dirname(sys.path[0]))
    path = os.path.join(parent_folder, data_set, power_folder, "Spectrum")
    os.chdir(path)
    files= glob.glob('*.txt')
    return files

def get_files_2(data_set, power_folder):
    parent_folder = os.path.dirname(os.path.dirname(sys.path[0]))
    power_folder_path = os.path.join(parent_folder, data_set, "Spectrum", power_folder)
    files = []
    for folder in os.listdir(power_folder_path):
        path = os.path.join(power_folder_path, folder)
        for file in os.listdir(path):
            files.append(os.path.join(power_folder_path, folder, file))
    return files

def get_detuning_files_dict_1(data_set, power_folder):
    files = get_files_1(data_set, power_folder)
    detunings = sorted(list(set([get_file_detuning_1(file) for file in files])), reverse=True)
    detuning_files_dict = {detuning: [] for detuning in detunings}
    for file in files:
        detuning_files_dict[get_file_detuning_1(file)].append(file)
    detuning_files_dict = sort_detuning_files_dict(detuning_files_dict)
    return detuning_files_dict, detunings

def get_detuning_files_dict_2(data_set, power_folder):
    files = get_files_2(data_set, power_folder)
    detunings = sorted(list(set([get_file_detuning_2(file) for file in files])), reverse=True)
    detuning_files_dict = {detuning: [] for detuning in detunings}
    for file in files:
        detuning_files_dict[get_file_detuning_2(file)].append(file)
    detuning_files_dict = sort_detuning_files_dict(detuning_files_dict)
    return detuning_files_dict, detunings

def get_file_contents(file):
    with open(file,'r') as f:
        file_contents=f.readlines()
    return file_contents

def sort_detuning_files_dict(detuning_files_dict):
    for detuning, file_list in detuning_files_dict.items():
        detuning_files_dict[detuning] = sorted(file_list)
    return detuning_files_dict

############################### PROCESS SPECTRUM FILES ###############################

def get_S21_from_file(file, power):
    raw_data = get_file_contents(file)
    voltage = get_voltage(raw_data)
    voltage = convert_to_mW(voltage)
    S21_detuning = get_S21_detuning(voltage, power)
    return S21_detuning

def get_voltage(data):
    voltage = [float(line.strip().split('\t')[0]) for line in data[1:]]
    voltage = array(voltage)
    return voltage

def get_frequency(detuning, detuning_files_dict):
    file = detuning_files_dict[detuning][0]
    raw_data = get_file_contents(file)
    frequency = [float(line.strip().split('\t')[1]) for line in raw_data[1:]]
    frequency = array(frequency)
    return frequency

def convert_to_mW(input_list):
    converted_list = (10**(input_list/10))/1000
    return converted_list

def get_S21_detuning(voltage, power):
    power_mW = convert_to_mW(power)
    S21 = voltage/power_mW
    return S21

def get_S21_normalised(S21_list, index_maxima):
    S21_normalised = [S21/S21[index] for S21, index in zip(S21_list, index_maxima)]
    return S21_normalised

############################### FILE HANDLING ###############################

def get_gamma(detuning, detuning_files_dict, power):
    frequency, S21_detunings = get_frequency_and_S21_detunings(detuning, detuning_files_dict, power)
    frequency, S21_offsets = get_frequency_and_S21_offsets(frequency, S21_detunings)
    S21_averages = get_S21_averages(S21_offsets)
    gamma = process_S21_averages(S21_averages, frequency, detuning, power)
    return gamma

def get_frequency_and_S21_detunings(detuning, detuning_files_dict, power):
    S21_detunings = [get_S21_from_file(file, power)
                         for file in detuning_files_dict[detuning]]
    frequency = get_frequency(detuning, detuning_files_dict)
    # plot_detunings_raw(S21_list_detuning, frequency)
    return frequency, S21_detunings

def get_frequency_and_S21_offsets(frequency, S21_detunings):
    index_maxima = [get_index_maximum(S21) for S21 in S21_detunings]
    frequency = get_offset_frequency(frequency, index_maxima)
    S21_offsets = get_S21_offsets(S21_detunings, index_maxima)
    S21_offsets = [restrict_domain(S21, min(index_maxima), 200) for S21 in S21_offsets]
    frequency = restrict_domain(frequency, min(index_maxima), 200)
    return frequency, S21_offsets

def get_S21_averages(S21_offsets):
    number_of_trials = len(S21_offsets)
    group_size = 5
    group_count = math.ceil(number_of_trials/group_size)
    S21_averages = [get_S21_average(group_number, group_size, S21_offsets)
                    for group_number in range(group_count)]
    return S21_averages

def get_S21_average(group_number, group_size, S21_offsets):
    left_index = group_number*group_size
    right_index = (group_number+1)*group_size
    S21_group = S21_offsets[left_index:right_index]
    test_group_valid(S21_group)
    group_average = np.mean(S21_group, axis=0)
    return group_average

def test_group_valid(S21_group):
    if len(S21_group) == 0:
        input("Group is empty: ")

def process_S21_averages(S21_averages, frequency, detuning, power):
    gamma_list = []
    for average_number, S21_average in enumerate(S21_averages):
        fitting_parameters, initial_fitting_parameters, flag_plot = fit(S21_average, frequency)
        title = f"Detuning: {detuning}, Power: {power}\nAverage number: {average_number}"
        print(title)
        #create_figure_1(S21_average, frequency, fitting=fitting_parameters, title=title)
        if flag_plot is True:
            fitting_parameters, data_accepted = fit_plot_manually(S21_average, frequency, fitting_parameters, initial_fitting_parameters)
            if data_accepted is False:
                continue
        gamma_list.append(abs(fitting_parameters[1]))
    if len(gamma_list) == 0:
        input("Gamma list is empty: ")
    return mean(gamma_list)

def get_index_maximum(S21):
    """
    We get a ballpark guess of where the peak is by using argmax Around this
    point we find assign a value to how good that point would work as the centre
    of the points using a weighted sum. The worse the point is, the higher the
    value of the heuristic. We get something that looks like y=|x| but with a
    rounded bottom. Using the data in the rounded region was less robust, so we
    define two lines from each side of the bottom in the region where the
    heuristic is better behaved and find where they intersect. This point is
    used as the centre.
    """
    first_guess = argmax(S21)
    left_x, right_x = max(0, first_guess-150), min(first_guess+150, len(S21)-1)
    candidates = list(range(left_x, right_x, 4))
    points = array(range(left_x, right_x))
    uncentred_heuristics = [get_uncentred_heuristic(S21, x, points) for x in candidates]
    m = argmin(uncentred_heuristics)
    x_m, y_m = get_heuristic_line_intersection(m, uncentred_heuristics)
    #plot_index_max_heuristic(candidates, uncentred_heuristics, x_m, y_m,
    #                         x_1, x_2, x_3, x_4, y_1, y_2, y_3, y_4)
    return candidates[x_m]

def get_uncentred_heuristic(S21, x, points):
    uncentred_heuristic = abs(x-points)*(S21[points])**2
    uncentred_heuristic = sum(uncentred_heuristic)
    return uncentred_heuristic

def get_heuristic_line_intersection(m, uncentred_heuristics):
    x_1, x_2, x_3, x_4 = m-15, m-14, m+14, m+15
    y_1, y_2, y_3, y_4 = (uncentred_heuristics[x] for x in [x_1, x_2, x_3, x_4])
    a, b, e = y_2-y_1, x_1-x_2, x_1*(y_2-y_1)+y_1*(x_1-x_2)
    c, d, f = y_4-y_3, x_3-x_4, x_3*(y_4-y_3)+y_3*(x_3-x_4)
    x_m = math.floor((d*e-b*f)/(a*d-b*c))
    y_m = (-c*e+a*f)/(a*d-b*c)
    return x_m, y_m

def plot_index_max_heuristic(candidates, uncentred_heuristics, x_m, y_m,
                             x_1, x_2, x_3, x_4, y_1, y_2, y_3, y_4):
    plt.figure(figsize=(80, 60))
    plt.plot(candidates, uncentred_heuristics)
    plt.plot(candidates[x_m], y_m, 'sr')
    plt.plot([candidates[x_1], candidates[x_2]], [y_1, y_2], '-r')
    plt.plot([candidates[x_3], candidates[x_4]], [y_3, y_4], '-r')
    plt.show()

def get_moving_average(points, window_width):
    N = len(points)
    window_points = [[points[inside_window(i+j, N)] for i in range(window_width)]
                     for j in range(N)]
    moving_average = array([sum(window)/window_width for window in window_points])
    return moving_average

def inside_window(i, N):
    if i < 0:
        return 0
    elif i > N-1:
        return N-1
    return i

def get_offset_frequency(frequency, index_maxima):
    min_index, max_index = min(index_maxima), max(index_maxima)
    frequency = frequency[0:len(frequency) - (max_index - min_index)]
    resonant_frequency = frequency[min_index]
    frequency -= resonant_frequency
    return frequency

def get_S21_offsets(S21_list, index_maxima):
    min_index, max_index = min(index_maxima), max(index_maxima)
    S21_offset_list = [get_S21_offset(S21, index, min_index, max_index)
                       for S21, index in zip(S21_list, index_maxima)]
    return S21_offset_list

def get_S21_offset(S21, index, min_index, max_index):
    left_index = index - min_index
    right_index = len(S21) - (max_index - index)
    S21_offset = S21[left_index:right_index]
    return S21_offset

def restrict_domain(S21, centre, width):
    left = centre - width
    right = centre + width
    S21 = S21[left:right]
    return S21

def create_figure_1(S21_list, frequency, filter_rate=1,
                    title="S21 vs frequency", fitting=None):
    S21_list = ensure_2D_list(S21_list)
    plt.close('all')
    #plt.figure(figsize=(80, 60))
    plt.figure()
    for index, S21 in enumerate(S21_list):
        if index % filter_rate == 0:
            plt.plot(frequency, S21,'.',alpha=1)
    plot_fitting(fitting, frequency)
    add_plot_labels(title)
    plt.show()

def plot_fitting(fitting, frequency):
    if fitting is not None:
        plt.plot(frequency,peval(frequency, fitting),'k--', alpha=0.5,linewidth=2.0,label='fit')

def plot_detunings_raw(S21_list_detuning, frequency):
    for i, S21 in enumerate(S21_list_detuning):
        max_x = get_index_maximum(array(S21))
        max_y = S21[max_x]
        plt.figure(figsize=(80, 60))
        create_figure_1(S21, frequency)
        plt.plot([frequency[max_x], frequency[max_x]], [0, max(S21)], 'r')
        plt.show()

def ensure_2D_list(test_list):
    if hasattr(test_list[0], '__iter__'):
        return test_list
    else:
        return [test_list]

def add_plot_labels(title):
    plt.title(title)
    x_ticks = plt.xticks()[0]
    max_x_tick = max(abs(x_ticks))
    prefix_power = math.floor(math.log(max_x_tick, 1000))
    prefix = {-1: "mHz", 0: "Hz", 1: "kHz", 2: "MHz", 3: "GHz", 4: "THz"}[prefix_power]
    x_labels = [f'{value:.0f}' for value in plt.xticks()[0]/1000**prefix_power]
    plt.xticks(x_ticks, x_labels)
    plt.xlabel('${\omega_c}$' + f'({prefix})')
    plt.ylabel('Amplitude')

def peval(freq,p):
    F, gamma, noise, w = p
    res = (F/(gamma**2+4*(freq-w)**2))+noise
    return res

def residuals(p,X,f):
    res=peval(f,p)-X
    return res

def fit(S21, frequency):
    initial_fitting_parameters = get_initial_fitting_parameters(S21, frequency)
    fitting_results = leastsq(residuals, initial_fitting_parameters, args=(S21,frequency), full_output=1)
    fitting_parameters = fitting_results[0]
    flag_plot = get_flag_plot(fitting_parameters, initial_fitting_parameters)
    return fitting_parameters, initial_fitting_parameters, flag_plot

def get_initial_fitting_parameters(S21, frequency):
    """
    We approximate the 4 fitting parameters
    Noise: most of the points are not at the peak so this is given by the average value
    Resonant frequency: this should be around 0 because we have centred it, but it usually
    sits around 2 (note this doesn't mean we have centred it badly - the purpose of that
    was to be able to average them in a reliable and robust way, having the resonant
    frequency at exactly 0 was a secondary goal to this)
    F and Gamma: after fixing the noise and resonant frequency we have two more degrees of
    freedom and we use two pieces of information from the data to find these.
    The first of these is the peak which we refer to as K. We assume this happens at
    resonance, and we say our fit peaks at K which is some fraction of the peak.
    The second of these is the "width". The fit intersects the line y = k in two places,
    and the difference of these is sqrt((K-k)/k) * Gamma which can be rearranged for Gamma.
    Now we know how to extract gamma from a width, we find the width by counting the number
    of points above y = k and dividing by the resolution of the x axis.
    Some values are multiplied by constants to get a better fit, and we also use a moving
    average to make things smoother first
    """
    end = int(len(S21)/5)
    noise, w = mean(S21[:end])/20, 2
    S21 -= noise
    K = np.mean(S21[S21 >= np.max(S21)*2/3])
    k = K * 1/3
    frequency_resolution = frequency[1] - frequency[0]
    peak_points = [S21 > k]
    width = 2 * (np.count_nonzero(peak_points) + 1)/frequency_resolution
    gamma = width * math.sqrt(k/(K-k))
    F = gamma**2 * K * 1/2
    initial_fitting_parameters = [F, gamma, noise, w]
    return initial_fitting_parameters

def get_flag_plot(fitting_parameters, initial_fitting_parameters):
    fit_ratio = fitting_parameters[:2]/initial_fitting_parameters[:2]
    fit_heuristic = sum(fit_ratio + 1/fit_ratio) + abs(fitting_parameters[3] - initial_fitting_parameters[3])
    if fit_heuristic > 20:
        print(f"Fit heuristic: {fit_heuristic}")
        return True
    return False

def fit_plot_manually(S21, frequency, fitting_parameters, initial_fitting_parameters):
    while True:
        for i, j in zip(["F", "Gamma", "Noise", "w"], fitting_parameters):
            print(f"{i}: {j}")
        create_figure_1(S21, frequency, fitting=fitting_parameters)
        prompt = ("\nWhich option do you want to change?\n1: F\n2: Gamma\n3: Noise\n" +
                  "4: w\n5: Reset to default\n6: Change all at once\n" +
                  "7: Attempt automatic fit\n8: Accept\nNo input: Reject\n")
        fitting_input_choice = input(prompt)
        if fitting_input_choice == "":
            return fitting_parameters, False
        elif fitting_input_choice in ["1", "2", "3", "4"]:
            prompt = "\nWhat is the new value you want to change it to: "
            try:
                new_parameter_value = float(input(prompt))
                fitting_parameters[int(fitting_input_choice)-1] = new_parameter_value
            except:
                pass
        elif fitting_input_choice == "5":
            fitting_parameters = list.copy(initial_fitting_parameters)
        elif fitting_input_choice == "6":
            prompt = "Enter all the new values in a list separated by spaces\n"
            input_wrong = True
            while input_wrong:
                try:
                    fitting_parameters = [float(parameter_input) for parameter_input in input(prompt).split(" ")]
                    input_wrong = False
                except:
                    print("Sorry, you typed it in wrong, try again")
        elif fitting_input_choice == "7":
            fitting_results = leastsq(residuals, fitting_parameters, args=(S21,frequency), full_output=1)
            fitting_parameters = fitting_results[0]
        elif fitting_input_choice == "8":
            return fitting_parameters, True
        else:
            print("Sorry, you must choose one of the options. Try again.")

def output_gamma(detunings, gamma_list, data_set, power_folder):
    output_path = prepare_output_path()
    file_name = os.path.join(output_path, f"gamma_vs_detuning_{data_set}_{power_folder}")
    with open(file_name, "w+") as file:
        file.writelines("Detuning\tGamma\n")
        for detuning, gamma, in zip(detunings, gamma_list):
            file.writelines(f"{detuning}\t{gamma}\n")

def prepare_output_path():
    parent_path = os.path.dirname(sys.path[0])
    output_path = os.path.join(parent_path, "Gamma Results")
    if os.path.isdir(output_path) is False:
        os.mkdir(output_path)
    return output_path


def process_experiment_1(data_set, power_folder):
    detuning_files_dict, detunings = get_detuning_files_dict_1(data_set, power_folder)
    power = int(power_folder[0:2])
    gamma_list = [get_gamma(detuning, detuning_files_dict, power) for detuning in detunings]
    output_gamma(detunings, gamma_list, data_set, power_folder)

def process_experiment_2(data_set, power_folder):
    detuning_files_dict, detunings = get_detuning_files_dict_2(data_set, power_folder)
    power = int(power_folder[0:2])
    gamma_list = [get_gamma(detuning, detuning_files_dict, power) for detuning in detunings]
    output_gamma(detunings, gamma_list, data_set, power_folder)

def iterate_through_power_levels_1(data_set):
    path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), data_set)
    for power_folder in os.listdir(path):
        process_experiment_1(data_set, power_folder)

def iterate_through_power_levels_2(data_set):
    path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), data_set, "Spectrum")
    for power_folder in os.listdir(path):
        process_experiment_2(data_set, power_folder)

"""
For data sets in the same format as 15112022, use version 1 of functions
For data sets in the same format as 16112022, use version 2 of functions
You should only ever need to change the number on iterate_through_power_levels_i
"""

#initial_fitting_parameters = [1e-9, 70, 1e-16, 2]
#initial_fitting_parameters = [5e-12, 5, 3e-15, 1.5]

data_set = "16112022_overnight"
#data_set = "15112022"
iterate_through_power_levels_2(data_set)

