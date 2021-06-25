# PrivacyContest
### Differential Privacy Temporal Map Challenge - Sprint 3

In the Differential Privacy Temporal Map Challenge (DeID2) the task is to develop algorithms that preserve data utility as much as possible while guaranteeing individual privacy is protected. The challenge features a series of coding sprints to apply differential privacy methods to temporal map data, where one individual in the data may contribute to a sequence of events. The goal is to create a privacy-preserving dashboard map that shows changes across different map segments over time.

Submissions are assessed based on:

1.  their ability to prove they satisfy differential privacy; and
2.  the accuracy of output data as compared with ground truth.

###  The Data

The main dataset includes quantitative and categorical information about 16 million taxi trips in Chicago, including time, distance, location, payment, and service provider. The data includes several features along with time segments (trip_day_of_week and trip_hour_of_day), map segments (pickup_community_area and dropoff_community_area), and simulated individuals (taxi_id). Solutions in this sprint produce a list of records (i.e. synthetic data) with corresponding time and map segments.

### Brief Algorithm Description

The main idea is to combine similar features in the pre-processing phase, create privatized histograms of the features, then during the post-processing phase create the simulated data. The individual taxis are created by simply counting the number of distinct taxi_ids, adding noise and then iterating through the privatized count. The number of trips per taxi_id is calculated by counting the distinct taxi_ids with k number of trips (k = 1-200) and adding noise to each bin.

A total of 5 queries are used:

1) Count of distinct taxi_ids
2) Count of distinct taxi_ids with k number of trips
3) Histogram of the proximity-shift-pca-dca feature by a sub-sample of taxi_id
4) Histogram of the company-payment_type feature by a sub-sample of taxi_id
5) Histogram of fare_codes feature by a sub-sample of taxi_id


A proximity dictionary is created containing a trip seconds estimate for each pca-dca combination. The proximity dictionary is used in the post-processing process to align the privatized data.

### Contents

#### src

- globals.py - global variables used to improve speed.
- main.py - the main program
- simulate_row.py - creates a row of simulated data
- utilities.py - a collection of eight functions for pre-processing, population (bin) creation and weight creation

#### other files

- writeup.pdf - contains documentation and an explanation for the algorithm including a mathematical privacy proof.
- requirements.txt - a pip dependency file

### Setup and Running the Code

The environment can be setup using requirements.txt or simply use python 3.8.5+ with the following packages:
pandas, numpy, json, pathlib, loguru, random.

Assuming you have the data and parameters files (ground_truth.csv and parameters.json) used in the competition, set the paths in the first 21 lines of code in main.py to correspond to your configuration.

Run the code: python main.py
