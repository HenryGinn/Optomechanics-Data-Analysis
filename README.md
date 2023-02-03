# Optomechanics-Data-Analysis

############# OVERVIEW #############

There are 3 main sets of programs
1: Side band fitting
2: Plot gamma
3: File name correctors

Side Band Fitting
This has 4 classes: DataSet, Power, Trial, Detuning. Side Band Fitting Interface handles these classes. This is the code that goes through the data and finds the value of gamma for each detuning and outputs to text files.

Plot Gamma
This reads the data from the files produced by the side band fitting code and produces a plot. Each of the powers is shown as a different line, and all data sets are included on one plot.

File Name Correctors
These are preprocessing programs that help make the file and folder names consistent and easily processed by other programs.

############# CHECKS TO RUN BEFORE USING #############

Main Folder Structure
All folder locations are defined relatively. The parent folder contains any data sets and a folder called "Repo". Inside "Repo" are one or two folders: one where all the files in the repository should be saved, and the other where the results are saved to (this is called "Gamma Results" but may not exist)

Data Set Folder Structure
Different data sets have different folder structures.
    For data sets in the same format as 15112022, use folder_structure_type=1
    For data sets in the same format as 16112022_overnight, use folder_structure_type=2
    For data sets in the same format as 19112022, use folder_structure_type=3

File Names
Find out what folder structure your data set has out of the options listed above. In the program you are using, check the notes that are made about that data set. The main causes of error are as follows
    1: Numberings such as 0, 1, ..., 10, 11. When sorting as a string this will get 0, 10, 1, 11, so numbers should be padded with leading 0s: 00, 01, ..., 10, 11.
    2: Missing underscores. Underscores are used to find positions in file names to extract information. Sometimes these are missing and need to be added
    3: Folders containing files of different sizes. If these are part of the same data set, they should have the same size. Incorrect sizes should be deleted from the folder (a copy of the data, not the original).

############# REVIEW OF ANALYSIS IN SIDE BAND FITTING #############

1: How to review the realignment of the plots so that the peak is at the centre before the average.
Go to the get_frequency_and_S21_detunings function and call the function plot_detunings_raw. For a given detuning, this will iterate through all the data that will be averaged together to make that detuning and plot each one, with a vertical red line drawn showing where it thinks the peak is.

2: How to review the computation of where the peak is.
At the end of the function get_index_maximum, call plot_index_max_heuristic. This will plot the shape the heuristic (should be like the function |x| but rounded at the bottom), two line segements on either side of the minimum (these should be on straight parts of the curve), and a red square at the bottom. This red square is where the minimum is. It will usually be directly below the minimum, but can be offset to the left. This is expected behaviour, and finds the minimum more accurately.

3: How to review the plots after the average has been taken.
At the end of get_gamma, call the function create_figure_1.

4: Manual fitting instructions
Deciding if a plot needs to be fitted manually: the initial fitting parameters are assumed to be somewhat reasonable, and a fitting heuristic is computed by how different the computed fitting parameters are from the initial. If this is above a certain threshold, it will be flagged and sent to be handled manually.
The figure will be plotted with the automatic fit. Close this figure and then a menu will appear asking what changes you want to make to the fitting parameters, or if you want to accept or reject the fit. If the data is wrong, or cannot be fitted sufficiently well, it should be rejected. You need to close the figures manually to move on to the next figure

############# NOTE ABOUT PLOTTING #############

If you are running in VS code, you need to be plotting in inline mode or it won't display. You won't be able to dynamically interact with the graph (such as reselecting a region).
If you are running in a browser, you can plot in notebook mode. Be careful as it will plot all of the results and can be very slow to use
Recommend to convert the notebook to a script - this will produce the plots one at a time and the next one appears when you close a plot.

############# CURRENT TASKS #############

1: Fix file names so they can be sorted easily DONE
2: Sort the file names for each detuning
3: 3 subplots needed.
Subplot 1: detuning vs time
Subplot 2: colourplot where each vertical strip is an S21 vs frequency relationship and time is on the horizontal axis
Subplot 3: colourplot where each vertical strip is a sideband plot (S21 vs frequency) and time is on the horizonal axis.