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

## Initialisation

The first thing to do is create a DataSet object which we will refer to as "my_data_set". This takes in the folder name of the data set you want to look at, and this will be form of either "ddmmyyyy" or "ddmmyyyy_overnight". When this object is created it will create objects in a hierarchy corresponding to the hierarchy of the data. The DataSet object will have a list of Drift objects, the Drift objects a list of Detuning objects, the Detuning objects a list of Group objects, and the Group objects a list of Spectrum objects which are a subset of Data. It will also create any missing results folders and set the paths of useful locations.

If you are running it from a terminal or shell then you will need to import "os", and use "os.chdir(path)" where the path is "{path of repository}/Frequency Comb Analysis". You will also need to provide an argument for script_path when creating the DataSet object.

## process_spectrum

This will read the data from the spectrum files so each Spectrum object will have "S21" and "frequency" attributes. It also computes the peak of each spectrum and uses this to assign a "S21" and "frequency" attributes to the group object by aligning the S21 of each Spectrum object and taking an average.

Possible change in the future: currently S21 and frequency are attributes of the Group object, but it may be beneficial to create a "spectrum" attribute of "Group" that was an instance of Spectrum.

## plot_spectra

This produces figures where each figure corresponds to a drift, and on each figure we have a set of subplots. Each subplot corresponds to a detuning, and on each subplot we have all the aligned S21 for each group plotted. Each subplot is created using semilogy.

This has two optional inputs. The first is "subplots", and prescribes how many subplots you want on each figure. The program may add more subplots to some figures so that each figure can have a roughly even number of subplots. The default value is None, and will result in all detunings being plotted on one figure. The other options is "drifts", and this takes in a slice, and integer, or an iterable object of integers. This allows the user to control which drifts they want to create plots of. It will slice or index into the list of drift objects which are ordered by drift value. The default value is None and will plot all drifts.

## To Do List