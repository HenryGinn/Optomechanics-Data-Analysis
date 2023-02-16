# Optomechanics-Data-Analysis

################################### CONTENTS ###################################

1: OVERVIEW
2: CHECKS TO RUN BEFORE USING
3: FOLDER STRUCTURE DESCRIPTION
4: REVIEW OF ANALYSIS IN SIDE BAND FITTING
5: COMPUTATION OF CENTRE OF DATA
6: TREATEMENT OF GAMMA AND OMEGA
7: TO DO LIST

################################### OVERVIEW ###################################

There are 3 main sets of programs 1: Side band fitting 2: Plot gamma and omega
3: File name correctors

Side Band Fitting
This has 5 main classes: DataSet, Power, Trial, Detuning, and Data, of which
Spectrum and Transmission are subclasses. Side Band Fitting Interface handles
these classes. This code centres the plots, extracts gamma from the data and
saves it to files, and produces various plots about the data.

Plot Gamma and Omega
This reads the data from the files produced by the side band fitting code and
produces a plot. Each of the trials from a data set is shown as a different line

File Name Correctors
These are preprocessing programs that help make the file and folder names
consistent and easily processed by other programs. The main issues are with
folder_structure_type=3 data sets, and these are fixed automatically by calling
the fix_folder_structure method of DataSet.

Main Folder Structure

Parent folder: everything is contained inside this one
    Repo: when saving the repository, this is the folder you want to clone to.
        Optomechanics-Data-Analysis: this is where all the scripts are saved.
        This folder will be made when you clone the repository to Repo
    Data Sets: contains all the raw data
        15112022: this contains all the information from that day of data
        collection
    Results: this folder will be created automatically when
    create_results_folder is called
        15112022: this is where all the results for that data set will be stored
            Omega results
                Text files: these contain the results for each trial
                Omega Plot: this is a plot of omega
            Gamma results
                Text files: these contain the results for each trial
                Gamma Plot: this is a plot of gamma

########################## CHECKS TO RUN BEFORE USING ##########################

Data Set Folder Structure:
Different data sets have different folder structures.
    For data sets in the same format as 15112022, use folder_structure_type=1
    For data sets in the same format as 16112022_overnight, use
    folder_structure_type=2
    For data sets in the same format as 19112022, use folder_structure_type=3
There are 3 areas in which the folder structure can change, see the doc string
in DataSet, Power, and Trial classes for more details.

File Names:
Find out what folder structure your data set has out of the options
listed above. In the program you are using, check the notes that are made about
that data set. The main causes of error are as follows
    1: Numberings such as 0, 1, ..., 10, 11. When sorting as a string this will
    get 0, 10, 1, 11, so numbers should be padded with leading 0s: 00, 01, ...,
    10, 11.
    2: Missing underscores. Underscores are used to find positions in file names
    to extract information. Sometimes these are missing and need to be added
    3: Folders containing files of different sizes. If these are part of the
    same data set, they should have the same size. Incorrect sizes should be
    deleted from the folder (a copy of the data, not the original).

It can be useful to only consider a single power, trial, detuning, or spectra.
Currently this is done manually by adding [0:1] on the end of the list
comprehension where the lists of objects are defined in set_power_objects (in
DataSet), set_trial_objects (in Power), set_detuning_objects (in Trial), and
set_spectrum_objects (in Detuning). These may have been left in for debugging
purposes.

######################### FOLDER STRUCTURE DESCRIPTION #########################

15112022 has a one folder for each power inside. Inside each of those are the
folders "Spectrum" and "Transmission. Inside "Spectrum" is a list of text files
with the data inside where each file has all the data for one detuning value.

16112022_overnight has two folders inside, "Spectrum" and "Transmission". Inside
each of those are folders for the powers, one folder per power. For "Spectrum",
inside of each power folder is a list of folders, one for each detuning. Inside
these is the list of text files with the data on the voltage vs frequency. Each
file is a separate run for that power at that detuning. For "Transmission",
inside each power folder is a list of text files. Each text file corresponds to
one of the detuning folders in "Spectrum". They can be matched up by their
timestamps

19112022 has two folders inside, "Spectrum" and "Transmission". Inside each of
those are folders for the powers, one folder per power. For "Spectrum", inside
of each power folder is a list of folders, one for each detuning. Inside each of
these for both "Spectrum" and "Transmission" is a list of folders, one for each
trial. These are named "{power}_{trial_number}". Inside each of these is the
same structure as in 16112022_overnight.

################### REVIEW OF ANALYSIS IN SIDE BAND FITTING ###################

1: How to review the realignment of the plots so that the peak is at the centre
before the average. In the Data class there is a class attribute called
"review_centre_results". Change this to true to review how well the computed
centre matches with the shape of the plot for all plots. When the data is
offsetted and realigned, it is necessary to chop off a bit from each end of the
range so that only the overlap region is considered. When this region is smaller
than expected, the plot will be reviewed.

2: How to review the computation of where the peak is. In the Data class there
is a class attribute called review_centre_heuristic. Change this to true to see
how the centre is being calculated. This will plot the shape the heuristic
(should be like the function |x| but rounded at the bottom), the points that
define the two line segements on either side of the minimum (these should be on
straight parts of the curve), and the intersection point of these lines. This
intersection is where the minimum is taken to be, and is where the centre is
chosen as. It will usually be directly below the minimum, but can be offset to
the left. This is expected behaviour, and finds the centre of the Lorentzian
more accurately. We note that the heuristic is usually only calculated for the 4
points that define the line, but it is computed for a range of points when
reviewing to construct the plot. For more details on this process, see the
section below titled "computation of centre of data"

3: How to review the plots after the average has been taken. Awaiting
implementation

4: Manual fitting instructions Deciding if a plot needs to be fitted manually:
the initial fitting parameters are assumed to be somewhat reasonable, and a
fitting heuristic is computed by how different the computed fitting parameters
are from the initial. If this is above a certain threshold, it will be flagged
and sent to be handled manually. The figure will be plotted with the automatic
fit. Close this figure and then a menu will appear asking what changes you want
to make to the fitting parameters, or if you want to accept or reject the fit.
If the data is wrong, or cannot be fitted sufficiently well, it should be
rejected. You need to close the figures manually to move on to the next figure

######################## COMPUTATION OF CENTRE OF DATA ########################

We compute the centre of the spectrum so we can shift all spectra within a
detuning trial and find the average. We expect this to be around the resonsant
frequency, but the value we compute is usually slightly to the left. Note that
the purpose of this step is not to find the resonant frequency perfectly, but to
assign a number to the centre reliably that leads to all spectra being realigned
accurately.

The first step is to get a very rough idea of where the peak is using argmax on
the S21 array. We then consider a region around this. The program will output a
warning if the peak is near the edge as this can lead to worse results when
finding the centre, and is usually from bad data. The peak should be very
safetly in the middle of the recorded frequency range.

For a selection of points in the computed region, a heuristic is computed that
says how uncentred that point is relative to the distribution, smaller numbers
being better. Plotting this gives a curve similar to |x| but with a rounded
bottom. This heuristic is just a weighted average of the distance of the other
points to x and the squared value of S21 at those points.

A naive choice of centre would be the minimum value of the heuristic described
above, but this is biased to the right. The heuristic plot is better behaved
away from the centre so on each side we define two lines that are roughly
tangent to the curve. We define the centre to be the point where these two lines
intersect. We currently define these two lines by interpolation through two
points per line, but a least squares fit could also be implemented.

This has a sound mathematical basis as if this process is done with a perfect
Lorentzian then you get a curve y = A*x*sin(arctan(x/B)) + C (C has some x
dependence but this is negligible and unimportant). If we approximate arctan(x)
as pi/2 for x away from 1 (this approximation is pretty good for x > 3) then we
see that our curve looks like |x| + c in the region we are interested in.

######################## TREATEMENT OF OMEGA AND GAMMA ########################

Each spectrum has a value of omega and each omega has an associated drift. We can take smaller groups of omega and average them, as this helps us account for the drift. We take the transmission before each spectrum to recalibrate the system to ensure it is being driven at the resonant frequency. When the spectrum data is taken, energy is put into the system which changes the resonant frequency so it needs to be recalibrated. As the spectra are taken, the system is becoming uncalibrated as the resonant frequency drifts. We find this drift by linear interpolation.

We note that it takes the same time to take each spectrum, so the spectrum files are linear in time. This means we need to be careful when we reject the values of omega from certain spectra as we need to interpolate based on what time it was taken. To avoid issues with this, the index of the spectrum file should be taken with respect to the original list of spectra, and you cannot get the index of an omega by finding it's index in the list of valid omega.

When taking the average of a group of omegas there are two ways of finding the drift of the average. The first is by taking the indexes of the spectra that the omegas within the group were taking from (the original set of spectra, including the omegas that have been rejected as outliers), taking the average of these indexes, dividing by the total number of spectra, and interpolating based on this. The second is take the index of each spectrum file the omega was calculated from, dividing by the total number of spectra, interpolating this to get the drift for that omega, and then averaging the drifts. These processes get the same results because the interpolation process is linear.

All the non-outlier omegas are stored in a text file where each row contains omega, it's detuning, and it's interpolated drift. As noted above we can find the average drift of the group by taking the average of these drifts and we do not run into issues. This means we don't need to include the index of the file that each omega was taken from, and we no longer need to be careful about whether the index is with respect to the list of all spectra, or the list of the spectra with the outlier omegas removed.

We split the omegas into groups and average each group of omegas. These are then saved in a file (one file per trial per group size) along with their detuning and average drift. When they are plotted, the files of all averages that have been found are plotted. These averages are found using the data saved in the original omega file described above. We note that the original file is not plotted, but if you want to plot it then you can compute the averaged omega with a group size of 1. The group size is indicated in the file name, and the original file is distinguished from the others by not having this.

Each spectrum is approximately in the shape of a Lorentzian curve. This has the
form of F/(gamma² + 4(frequency - resonant frequency)²) + noise. Gamma affects
how wide the peak is and we find this value by fitting a Lorentzian to it.

Fill in: explanation of how intial fitting parameters are found

################################## TO DO LIST ##################################

Record all values of omega before averaging. Each row in the file will need to have the value of omega, the drift, and also it's time interpolation value as this will be needed later. The plotting code will need to be changed drastically, it was from the old version and has been crowbarred into the new class based structure so this is not unexpected.

Save the S21 results to files

Process gamma in a similar way to omega

Make subplots of gamma and omega