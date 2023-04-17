# Optomechanics Data Analysis

## Contents

1. [Overview and Usage](#overview-and-usage)
1. [Side Band Fitting](#side-band-fitting)
1. [Transmission Analysis](#transmission-analysis)
1. [Frequency Comb Analysis](#frequency-comb-analysis)
1. [To Do List](#to-do-list)

## Overview and Usage

Parent folder: everything is contained inside this one
    Repo: when saving the repository, this is the folder you want to clone to.
        Optomechanics-Data-Analysis: this is where all the scripts are saved.
        This folder will be made when you clone the repository to Repo
    Data Sets: contains all the raw data
        ddmmyyyy: this contains all the information from dd/mm/yyyy
    Side Band Results: anything produced by Side Band Fitting will be saved here
    Transmission Results: anything produced by Transmission will be saved here
    Frequency Comb Results: anything produced by Frequency Come Analysis will be saved here.

## Side Band Fitting

This part of the program handles spectra measured at a range of detunings and is controlled by "Side Band Analysis Interface". Below are a range of its features

- Find $\Omega_m$ and $\Gamma_m$
- Create plots of $\Omega_m$ and $\Gamma_m$ against detuning
- Align multiple spectra and average them together

Known relevant data sets:
- 15112022
- 16112022_overnight
- 17112022
- 18112022
- 19112022
- 21112022
- 22112022

## Transmission Analysis

This part of the program looks at transmission curves and is controlled by "Transmission Analysis Interface". Below are a range of its features

- Plot groups of transmission curves overlayed on top of each other with no processing, either before any processing or after they have been aligned. The number of lines on each subplot and the number of subplots can be specified.

Known relevant data sets:
- 14112022

## Frequency Comb Analysis

This part of the program looks at data over a wider frequency range where you can see the other sidebands.

Known relevant data sets:
- 06122022_overnight

## To Do List

- Update folder structure in all of the docs