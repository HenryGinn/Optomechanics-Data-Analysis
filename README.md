# Optomechanics-Data-Analysis

## Contents

---

1. [Overview](#overview)
1. [Program Files](#program-files)
    1. [Main Level](#main-level)
    1. [Power](#power)
    1. [Trial](#trial)
    1. [Detuning](#detuning)
    1. [Data](#data)
1. [Checks to Run Before Use](#checks-to-run-before-use)
1. [Folder Structure Description](#folder-structure-description)
1. [Processing of Spectrum Data](#processing-of-spectrum-data)
1. [Review of Analysis in Sideband Fitting](#review-of-analysis-in-sideband-fitting)
1. [Computation of Centre of Data](#computation-of-centre-of-data)
1. [Treatment of Omega and Gamma](#treatment-of-omega-and-gamma)
1. [To Do List](#to-do-list)

---

## Overview

### Structure of Data

The program has a hierarchy that corresponds to the hierarchy of the data
- Interface: this is where you control what the program does. In the finished program the user should only ever need to interact with this script
- Data set: this corresponds to the data collected in one session. The data sets are stored in folders with names like 15112022
- Power: the power that an experiment runs at can vary and these are stored in more folders. The powers used usually range from 24 dBm to 29 dBm
- Trial: for each power there can be multiple runs of the same experiment, and we call each of these runs a trial
- Detuning: for each trial the experiment looks at a specific value for the detuning. The detunings usually range from -20 MHz to 20 MHz.
- Data: the output power is measured at a range of frequencies, and this is used to calculate something called the S21 - we convert it immediately and only ever work in terms of S21. There are two types of data taken: the transmission is taken over a wide frequency range and locates the resonant frequency of the cavity, and each spectrum measures a narrow region around the peak when the cavity is pumped at some detuning from the resonant frequency.

### General Procedure for Processing Data

Data is read from the relevant places, and automatic checks are done to see whether each bit of data needs to be reviewed. Flagged data can be automatically rejected or manually reviewed, or all data can be reviewed instead of just the parts the program suggested as problematic. This data is then saved to a file. Where potentially useful, intermediate steps are saved to files to avoid needing to rerun code.

---

## Program Files

These are the programs at each of the levels described in the overview.

[Main Level](#main-level)
- Side Band Fitting Interface
- Utils

[Data Set](#data-set)
- DataSet
- PlotGammaAndOmega
- PutTrialsInFolders

[Power](#power)
- Power

[Trial](#trial)
- Trial
- TrialPlot
- OmegaTrial
- GammaTrial

[Detuning](#detuning)
- Detuning
- DetuningPlot
- AverageDetuning
- OmegaDetuning
- GammaDetuning

[Data](#data)
- Data
- DataFit
- Transmission
- Spectrum
- AverageData

### Main Level

#### Interface

The process of analysing the data is split into parts. The first step is to analyse the folder structure, and this will create the necessary hierarchy of objects that the rest of the program can use. It also creates any folders that might be used to store results.

Processing the transmission and the spectra happens next, and the peaks of the S21 are saved to text files. If the peak of the S21 curve is problematic on an inital inspection, the data will not be saved. Whenever some data is needed at a later stage, it loads the data from these files, and it will already have a guarantee the data is not too bad. These only need to be run once per data set.

The handling of omega happens next. Whenever omega is processed, the omega objects need to be created so this method should be run. The process_omega method will find a value of omega for each spectrum and save it to a text file, along with it's drift - these files have the label "All" at the end. The average_omega method will read these omega from a file and average them in group sizes specified by the argument of the method. If no average size is given then all the omega will be averaged. The results are saved to text files along with the standard deviation associated with the averaging procedure. The plot_omega method will take all the averaged omega files for each trial and plot them on a graph. Omega objects do not need to be created for plotting.

Gamma is handled in a similar way to omega. The main difference is that getting gamma requires a fit of the spectra to be found, but the data is often quite messy so fitting each spectrum will often give bad fits. Also they cannot be averaged in the same way as omega as the fitting process is non-linear, and cannot be interchanged with the averaging process. Several spectra are aligned and averaged together, and a fit of this gives a value of gamma. For each new average size the process_gamma method will need to be called, and as with omega, if no average size is given then all spectra will be used. The average_gamma method takes the results from the previous step and averages them together for each detuning. We also get a standard deviation associated with this average. Plotting works similarly to omega.

The final set of methods are to create plots. The plot_omega_and_gamma method creates a plot with both omega and gamma on two axes within one figure, and these individual plots are the same that you would get from plot_omega and plot_gamma. You can also plot things where there is one plot per trial with the create_trial_plots method, or plot things at the detuning level with the create_detuning_plots method. Both of these take in a string that gives the type of plot desired.

#### Utils

This has any functions that are useful in general and can be used across the program. Currently it does not have much in there but there are several things that should probably be in there when cleaning up.

---

### Data Set

#### DataSet

The main task of the DataSet class is to take in the requests from the interface and manage them. It keeps track of the power objects, the paths of the main folders associated with the data set, and mainly calls methods of the power objects. Power and PutTrialsInFolders are the managed here.

#### PutTrialsInFolders

Some of the later side band data sets have badly managed folders. For the folder structure where the experiment has been split into trials, the program expects to find one folder per power, and inside each of those, one folder per trial labelled {power}_{trial_number}. When this program is called it will detect whether the issue is present, and if it is fix them after asking the user if they want it to go ahead.

#### Fix numbering on 29 dBm trials in 19112022

This is a separate script that is not managed by DataSet. After the program has claimed to fix the folder names, this will need to be run to handle this edge case. I deemed it not worth it to automatically detect this situation. The issue it fixes is that there are 11 trials where the first one failed and so needs to be deleted, but then the numbering for the others is offset by 1.

---

### Power

#### Power

The Power class does not do much, and most of the things you might think are associated with the power level are actually handled at the trial level. It has two main jobs, one being the creation of the trial objects, and the other being calling the methods of the trial objects when it receives calls from the DataSet class.

---

### Trial

#### Trial

This is where most of the reading and writing of information about the transmission and the spectrum happens. One of it's main jobs is to create the detuning objects. It is at this stage where the transmission files need to be paired up with the spectrum files, and this is done by reading the timestamp. For each detuning there is one transmission and there can be many spectrum files.

The other main purpose of this class is to manage the collection of data about the transmission and spectra files (through the process_transmission and process_spectrum methods of DataSet) and save them to files. When this information needs to be accessed, the reading of those files will also be processed by this class. Whenever anything else needs to be processed at the trial level, they will refer to the attributes of the objects of this class as that is where the data is stored. For example, omega and gamma are found in GreekTrial, and one the attributes of this class is the trial object it is associated with, and that is how the class interacts with the trial data.

#### GreekTrial

This is where all handling of omega and gamma is handled at the trial level. It organises the finding of quantities to do with omega and gamma, saving them to files, and also reading them from files. It has two main functions which are called using the methods process_greek(average=None) and average_greek. It is also used when plotting omega and gamma, as that data will need to be read from the files in order to plot them. Each data series of is stored as an instance of the Greek class.

#### TrialPlot

This class if used for plotting anything at the trial level, apart from omega and gamma. 

#### GreekFigure

#### GreekAxis

---

### Detuning

#### Detuning

#### DetuningPlot

#### AverageDetuning

#### OmegaDetuning

#### GammaDetuning

---

### Data

#### Data
#### DataFit
#### Transmission
#### Spectrum
#### AverageData
---

## Checks to Run Before Use

### Data Set Folder Structure

Different data sets have different folder structures.
    For data sets in the same format as 15112022, use folder_structure_type=1 For data sets in the same format as 16112022_overnight, use folder_structure_type=2
    For data sets in the same format as 19112022, use folder_structure_type=3
There are 3 areas in which the folder structure can change, see the doc string in DataSet, Power, and Trial classes for more details.

### File Names

Find out what folder structure your data set has out of the options listed above. In the program you are using, check the notes that are made about that data set. The main causes of error are as follows
    1: Numberings such as 0, 1, ..., 10, 11. When sorting as a string this will get 0, 10, 1, 11, so numbers should be padded with leading 0s: 00, 01, ..., 10, 11.
    2: Missing underscores. Underscores are used to find positions in file names to extract information. Sometimes these are missing and need to be added
    3: Folders containing files of different sizes. If these are part of the same data set, they should have the same size. Incorrect sizes should be deleted from the folder (a copy of the data, not the original).

### Manual Filtering of Structures

It can be useful to only consider a single power, trial, detuning, or spectra. Currently this is done manually by adding [0:1] on the end of the list comprehension where the lists of objects are defined in set_power_objects (in DataSet), set_trial_objects (in Power), set_detuning_objects (in Trial), and set_spectrum_objects (in Detuning). These may have been left in for debugging purposes.

---

## Folder Structure Description

### Main Folder Structure

Parent folder: everything is contained inside this one
    Repo: when saving the repository, this is the folder you want to clone to.
        Optomechanics-Data-Analysis: this is where all the scripts are saved.
        This folder will be made when you clone the repository to Repo
    Data Sets: contains all the raw data
        15112022: this contains all the information from that day of data collection
    Results: this folder will be created automatically when
    create_results_folder is called
        15112022: this is where all the results for that data set will be stored
            Omega results
                Text files: these contain the results for each trial
                Omega Plot: this is a plot of omega
            Gamma results
                Text files: these contain the results for each trial
                Gamma Plot: this is a plot of gamma

### Data Set Folder Structures

The program knows about 3 types of folder structure and examples of each are given below. These are referred to as folder_structure_type = 1, 2, and 3. The program does not currently attempt to deduce what the folder structure is so this part has to be done manually.

15112022 has a one folder for each power inside. Inside each of those are the folders "Spectrum" and "Transmission. Inside "Spectrum" is a list of text files with the data inside where each file has all the data for one detuning value.

16112022_overnight has two folders inside, "Spectrum" and "Transmission". Inside each of those are folders for the powers, one folder per power. For "Spectrum", inside of each power folder is a list of folders, one for each detuning. Inside these is the list of text files with the data on the voltage vs frequency. Each file is a separate run for that power at that detuning. For "Transmission", inside each power folder is a list of text files. Each text file corresponds to one of the detuning folders in "Spectrum". They can be matched up by their timestamps

19112022 has two folders inside, "Spectrum" and "Transmission". Inside each of those are folders for the powers, one folder per power. For "Spectrum", inside of each power folder is a list of folders, one for each detuning. Inside each of these for both "Spectrum" and "Transmission" is a list of folders, one for each trial. These are named "{power}_{trial_number}". Inside each of these is the same structure as in 16112022_overnight.

---

## Processing of Spectrum Data

There are two things we want from each spectrum: the frequency of the peak and the value of Gamma when we fit it. The main issue we have is when the data is bad. Below we quantify some of the ways in which data can be bad or awkward
	1: No clear peak is present - the data just looks like noise
	2: The peak is in a very different place compared to the rest of the spectra for a given detuning. This means that when we align the spectra for analysing, we will need to cut off a lot of the data. This mainly happens when issue (1) happens and some noise is chosen as the peak, so once those spectra have been filtered out we should not expect to see this issue occuring.
	3: The peak is extremely narrow. Here the peak consists of only a handful of points, although they are still valid spectra and we want to keep them.

The first thing we want to do with the spectra is filter out the bad files (those affected by issues (1) and (2)). As we need to use the peaks to test whether they are valid, we remove those spectra at the same time as we are finding the peaks. After this stage the results will be saved to text files for each trial where each row contains the detuning, index of the peak, frequency of the peak, and the file number it came from. All these spectra should have well defined peaks in the expected positions and will be ready to be averaged together for fitting. This is implemented in two parts: the value of the noise and the actual peak are found and their ratio is computed. If it is beyond a certain threshold it is rejected - due to the very large number of spectra, this should not be done manually ever. Once a spectrum has been certified as having a high enough peak, the index of the peak is compared to the rest of the spectra that passed, and a modified standard deviation based on the median is used to determine which spectra are outliers.

## Review of Analysis in Sideband Fitting

---

1: How to review the realignment of the plots so that the peak is at the centre before the average. In the Data class there is a class attribute called "review_centre_results". Change this to true to review how well the computed centre matches with the shape of the plot for all plots. When the data is offsetted and realigned, it is necessary to chop off a bit from each end of the range so that only the overlap region is considered. When this region is smaller than expected, the plot will be reviewed.

2: How to review the computation of where the peak is. In the Data class there is a class attribute called review_centre_heuristic. Change this to true to see how the centre is being calculated. This will plot the shape the heuristic (should be like the function |x| but rounded at the bottom), the points that define the two line segements on either side of the minimum (these should be on straight parts of the curve), and the intersection point of these lines. This intersection is where the minimum is taken to be, and is where the centre is chosen as. It will usually be directly below the minimum, but can be offset to the left. This is expected behaviour, and finds the centre of the Lorentzian more accurately. We note that the heuristic is usually only calculated for the 4 points that define the line, but it is computed for a range of points when reviewing to construct the plot. For more details on this process, see the section below titled "computation of centre of data"

3: How to review the plots after the average has been taken. Awaiting implementation

4: Manual fitting instructions. Deciding if a plot needs to be fitted manually: the initial fitting parameters are assumed to be somewhat reasonable, and a fitting heuristic is computed by how different the computed fitting parameters are from the initial. If this is above a certain threshold, it will be flagged and sent to be handled manually. The figure will be plotted with the automatic fit. Close this figure and then a menu will appear asking what changes you want to make to the fitting parameters, or if you want to accept or reject the fit. If the data is wrong, or cannot be fitted sufficiently well, it should be rejected. You need to close the figures manually to move on to the next figure

---

## Computation of Centre of Data

We compute the centre of the spectrum so we can shift all spectra within a detuning trial and find the average. We expect this to be around the resonsant frequency, but the value we compute is usually slightly to the left. Note that the purpose of this step is not to find the resonant frequency perfectly, but to assign a number to the centre reliably that leads to all spectra being realigned accurately.

The first step is to get a very rough idea of where the peak is using argmax on the S21 array. We then consider a region around this. The program will output a warning if the peak is near the edge as this can lead to worse results when finding the centre, and is usually from bad data. The peak should be very safetly in the middle of the recorded frequency range.

For a selection of points in the computed region, a heuristic is computed that says how uncentred that point is relative to the distribution, smaller numbers being better. Plotting this gives a curve similar to |x| but with a rounded bottom. This heuristic is just a weighted average of the distance of the other points to x and the squared value of S21 at those points.

A naive choice of centre would be the minimum value of the heuristic described above, but this is biased to the right. The heuristic plot is better behaved away from the centre so on each side we define two lines that are roughly tangent to the curve. We define the centre to be the point where these two lines intersect. We currently define these two lines by interpolation through two points per line, but a least squares fit could also be implemented.

This has a sound mathematical basis as if this process is done with a perfect Lorentzian then you get a curve y = A*x*sin(arctan(x/B)) + C (C has some x dependence but this is negligible and unimportant). If we approximate arctan(x) as pi/2 for x away from 1 (this approximation is pretty good for x > 3) then we see that our curve looks like |x| + c in the region we are interested in.

---

## Treatment of Omega and Gamma

Each spectrum has a value of omega and each omega has an associated drift. We can take smaller groups of omega and average them, as this helps us account for the drift. We take the transmission before each spectrum to recalibrate the system to ensure it is being driven at the resonant frequency. When the spectrum data is taken, energy is put into the system which changes the resonant frequency so it needs to be recalibrated. As the spectra are taken, the system is becoming uncalibrated as the resonant frequency drifts. We find this drift by linear interpolation.

We note that it takes the same time to take each spectrum, so the spectrum files are linear in time. This means we need to be careful when we reject the values of omega from certain spectra as we need to interpolate based on what time it was taken. To avoid issues with this, the index of the spectrum file should be taken with respect to the original list of spectra, and you cannot get the index of an omega by finding it's index in the list of valid omega.

When taking the average of a group of omegas there are two ways of finding the drift of the average. The first is by taking the indexes of the spectra that the omegas within the group were taking from (the original set of spectra, including the omegas that have been rejected as outliers), taking the average of these indexes, dividing by the total number of spectra, and interpolating based on this. The second is take the index of each spectrum file the omega was calculated from, dividing by the total number of spectra, interpolating this to get the drift for that omega, and then averaging the drifts. These processes get the same results because the interpolation process is linear.

All the non-outlier omegas are stored in a text file where each row contains omega, it's detuning, and it's interpolated drift. As noted above we can find the average drift of the group by taking the average of these drifts and we do not run into issues. This means we don't need to include the index of the file that each omega was taken from, and we no longer need to be careful about whether the index is with respect to the list of all spectra, or the list of the spectra with the outlier omegas removed.

We split the omegas into groups and average each group of omegas. These are then saved in a file (one file per trial per group size) along with their detuning and average drift. When they are plotted, the files of all averages that have been found are plotted. These averages are found using the data saved in the original omega file described above. We note that the original file is not plotted, but if you want to plot it then you can compute the averaged omega with a group size of 1. The group size is indicated in the file name, and the original file is distinguished from the others by not having this.

Each spectrum is approximately in the shape of a Lorentzian curve. This has the form of F/(gamma² + 4(frequency - resonant frequency)²) + noise. Gamma affects how wide the peak is and we find this value by fitting a Lorentzian to it.

Fill in: explanation of how intial fitting parameters are found

---

## To Do List

- Clean code
- Update documentation

## Gamma class structure

OmegaTrial handles all the stuff to do with omega, and GammaTrial handles all the stuff to do with Gamma. There are things in common to both of these so they should be subclasses of a GreekTrial class. A greek can have several different files associated with it at the trial level, and these should all be able to be plotted on the same graph.

The TrialPlot class handles figures, and the PlotGreek class handles axes. This means that instances of the PlotGreek class should be handled by TrialPlot. PlotGreek should take in a GreekLine object and plot that line as multiple lines can be plotted on the same axis. The PlotGreek class should handle all labels as this is something associated with an axis, but it will be told to add labels by the TrialPlot class.