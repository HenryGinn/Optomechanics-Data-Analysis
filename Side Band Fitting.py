#!/usr/bin/env python
# coding: utf-8

# In[100]:


import os
import sys
from scipy import optimize
from scipy.optimize import leastsq
from numpy import *
import glob
from matplotlib import *
from pylab import *
import math

import matplotlib.font_manager as fm
font_names = [f.name for f in fm.fontManager.ttflist]
# mpl.rcParams['font.family'] = 'Times'
# mpl.rcParams['mathtext.fontset'] = 'custom'
# mpl.rcParams['mathtext.rm'] = 'Times'
# mpl.rcParams['mathtext.it'] = 'Times:italic'
# mpl.rcParams['mathtext.bf'] = 'Times'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]


# In[101]:


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
    print(data_set, power_folder, path)
    os.chdir(path)
    files= glob.glob('*.txt')
    return files

def get_files_2(data_set, power_folder):
    parent_folder = os.path.dirname(os.path.dirname(sys.path[0]))
    power_folder_path = os.path.join(parent_folder, data_set, "Spectrum", power_folder)
    files = []
    for folder in os.listdir(power_folder_path):
        path = os.path.join(power_folder_path, folder)
        print(data_set, power_folder, path)
        for file in os.listdir(path):
            files.append(os.path.join(power_folder_path, folder, file))
    return files

def get_detuning_files_dict_1(data_set, power_folder):
    files = get_files_1(data_set, power_folder)
    detunings = sorted(list(set([get_file_detuning_1(file) for file in files])), reverse=True)
    detuning_files_dict = {detuning: [] for detuning in detunings}
    for file in files:
        detuning_files_dict[get_file_detuning_1(file)].append(file)
    return detuning_files_dict, detunings

def get_detuning_files_dict_2(data_set, power_folder):
    files = get_files_2(data_set, power_folder)
    detunings = sorted(list(set([get_file_detuning_2(file) for file in files])), reverse=True)
    detuning_files_dict = {detuning: [] for detuning in detunings}
    for file in files:
        detuning_files_dict[get_file_detuning_2(file)].append(file)
    return detuning_files_dict, detunings

def get_file_contents(file):
    with open(file,'r') as f:
        file_contents=f.readlines()
    return file_contents


# In[102]:


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


# In[103]:


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
    #print(len(S21_group))
    group_average = np.mean(S21_group, axis=0)
    return group_average

def process_S21_averages(S21_averages, frequency, detuning, power):
    gamma_list = []
    for average_number, S21_average in enumerate(S21_averages):
        fitting_parameters = fit(S21_average, frequency)
        gamma_list.append(fitting_parameters[1])
        title = f"Detuning: {detuning}, Power: {power},\nAverage number: {average_number}"
        if fitting_parameters[1] > 200:
            create_figure_1(S21_average, frequency, title=title, fitting=fitting_parameters)
    return mean(gamma_list)


# In[104]:


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
    if first_guess > len(S21)-160:
        plt.plot(S21)
        plt.show()
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


# In[105]:


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


# In[106]:


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
    #plt.xlim(-2*10**7, 3.5*10**7)
    x_ticks = plt.xticks()[0]
    x_labels = [f'{value:.0f}' for value in plt.xticks()[0]/10**3]
    plt.xticks(x_ticks, x_labels)

def plot_figure_1(frequency, voltage):
    plt.plot(frequency, voltage,'.',alpha=1)
    plt.xlabel('${\omega_c}$ (kHz)')
    plt.ylabel('Amplitude')


# In[107]:


def peval(freq,p):
    F, gamma, noise, w = p
    res = (F/(gamma**2+4*(freq-w)**2))+noise
    return res

def residuals(p,X,f):
    res=peval(f,p)-X
    return res

def fit(S21, freq):
    p0=[10e-10, 20, 0.6e-14, 0]
    #p0=[7e-10, 3.53181220e+01, 5.69756968e-14, 4.02844320e+09]
    # The second parameter in p_final is Gamma_m
    plsq=leastsq(residuals,p0,args=(S21,freq),full_output=1)
    fitting_parameters = plsq[0]
    print(plsq[1])
    return fitting_parameters


# In[108]:


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


# In[109]:


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


# In[110]:


"""
For data sets in the same format as 15112022, use version 1 of functions
For data sets in the same format as 16112022, use version 2 of functions
You should only ever need to change the number on iterate_through_power_levels_i
"""
data_set = "16112022_overnight"
iterate_through_power_levels_2(data_set)

