# Frequency Comb Analysis

## Contents

1. [Overview](#overview)
1. [Initialisation](#initialisation)
1. [process_spectrum](#process_spectrum)
1. [plot_spectra](#plot_spectra)
1. [To Do List](#to-do-list)

## Overview

This program looks at the data in the following data sets (list not neccessarily complete)

- 06122022_overnight

Frequency combs are where you have large regular peaks and the envelope of these peaks is roughly an upside down $|x|$ shape. This document describes how to use the script "Frequency Comb Analysis Interface". It is where the program is controlled from.

Each of the functions of this program go into their own class and are subclasses of CombFunction. They have three basic actions: save, load, and plot (some do not have "plot" implemented). When the plot command is given, it attempts to load the data. When the load command is given and the data has not been saved, it will instead save the data. There are two reasons for this. Firstly, once the data has been generated it is much quicker to load it from a file the next time it is needed. To generate the data it may need data from many other functions, and all of those functions may need to generate the data. Secondly, if function A needs data from function B, but not function C, and function B needs data from function C, then when it runs the first time, functions A, B, and C will be run. Any future times it is run however, function A only needs to request the data from function B is loaded, and function C does not need to be loaded. With the structure used, data is only generated or loaded when necessary. The logic for this is implemented in the CombFunction parent class and the "load_necessary_data_for_saving" method in each subclass (if needed).

Each function should modify some of the drift, detuning, and group objects. The affect on these objects after saving and the affect after loading should be the same. For example when finding the coordinates of the peaks, each group object now has a spectrum object which has attributes which contain information about the peaks. All this data should be saved, and all of it set when it is loaded. This is done so that whether the data for a function was set via saving or by loading, all the necessary data will still be there. If the function has a plot feature, any data used for the plot should also be saved so the plots can be easily created once the data has been generated once.

## Initialisation

The first thing to do is create a DataSet object which we will refer to as "data_set". This takes in the folder name of the data set you want to look at, and this will be form of either "ddmmyyyy" or "ddmmyyyy_overnight". When this object is created it will create objects in a hierarchy corresponding to the hierarchy of the data. The DataSet object will have a list of Drift objects, the Drift objects a list of Detuning objects, the Detuning objects a list of Group objects, and the Group objects a list of Spectrum objects which are a subset of Data. It will also create any missing results folders and set the paths of useful locations.

If you are running it from a terminal or shell then you will need to import "os", and use "os.chdir(path)" where the path is "{path of repository}/Frequency Comb Analysis". You will also need to provide an argument for script_path when creating the DataSet object.

## Functions

### SpectraPeak

This function identifies the centre peak by using a simple argmax. It saves the amplitude, the frequency, and the index of the peak. It takes no kwargs and has no plot functionality.

### AlignSpectra

Each group has a list of spectra. This function takes each of those groups, aligns them all together, and then averages the values. It aligns them based on the frequency of the main peak, and it loads data from SpectraPeak for this. Takes in no kwargs and has no plot functionality implemented. Plotting of the spectra is a special case and is handled by PlotSpectra.

### AverageGroups

This is similar to what AlignSpectra does, but instead of taking the spectra associated to a group and averaging them, it takes the spectra associated with the groups associated with a detuning and averages them (this means each detuning object now has a spectrum object associated with it). The spectra are already aligned. This is done because the groups were very similar and doing the analysis separately for each group was not deemed worth it. The functionality in PlotSpectra to verify this was changed when AverageGroups was implemented, but there are pictures of the plots on slack.

### NoiseThreshold

There is some noise in the data and the aim of this function is to find a curve where everything above that can be reasonably safetly guaranteed not to be noise, while still being able to capture the lower peaks. The noise threshold is this curve, and is not the average level of the noise. The implementation of this may seem unnecessarily costly, but the previous implementation using a straight horizontal line was not sufficient. This is because the noise floor around the centre peak is higher up, and pushes the noise threshold too high to capture the lower peaks at the edges. Takes in no kwargs and can be seen on plots by passing "noise=True" into PlotSpectra.

### PeakCoordinates

This aims to identify where the peaks are. It identifies everything above the noise threshold as being part of a peak. Several points can define a peak, and the main computation is decomposing the set of all points into groups where each group of points is associated with one peak. It does this by taking advantage of the fact that points that are associated with one peak are going to be very close to each other. Once it has identified groups of points asssociated with each peak, it takes the maximum within each group to be the definition of the peak. Takes in no kwargs, and can be seen in plots by passing "markers=True" into PlotSpectra.

### PeakGaps

This finds the frequency gap between adjacent peaks

## To Do List