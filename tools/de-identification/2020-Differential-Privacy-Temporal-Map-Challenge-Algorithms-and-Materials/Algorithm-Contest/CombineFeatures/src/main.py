# Imports
import pandas as pd
import json
from pathlib import Path
from loguru import logger
from random import choices

import globals
import utilities
from simulate_row import simulate_row

# Set paths and directories for loading data and parameters
ROOT_DIRECTORY = Path("/codeexecution")
RUNTIME_DIRECTORY = ROOT_DIRECTORY / "submission"
DATA_DIRECTORY = ROOT_DIRECTORY / "data"

NOT_USED_IN_SUBMISSION = ("trip_hour_of_day", "trip_day_of_week")

ground_truth_file = DATA_DIRECTORY / "ground_truth.csv"
parameters_file = DATA_DIRECTORY / "parameters.json"
output_file = ROOT_DIRECTORY / "submission.csv"


# main progam
def main():

    with parameters_file.open("r") as fp:
        parameters = json.load(fp)

    # Initialize parameters - mrpi is max_records_per_individual
    max_records = parameters['runs'][0]['max_records']
    # mrpi = parameters['runs'][0]['max_records_per_individual']
    dtypes = {column_name: d["dtype"] for column_name, d in parameters["schema"].items()}

    epsilons = [run["epsilon"] for run in parameters["runs"]]
    columns = [k for k in parameters["schema"].keys() if k not in NOT_USED_IN_SUBMISSION]
    headers = ["epsilon"] + columns

    # Read and pre-process the ground truth
    logger.info("begin pre-processing")
    gt = pd.read_csv(ground_truth_file, dtype=dtypes)
    ground_truth = utilities.pre_process(gt)
    logger.info("end pre-processing")

    counter = 0
    e_counter = 1
    filenames = []

    # main for loop
    for epsilon in epsilons:
        # Create dataframe for final results and initialize lists
        front_list = []
        end_list = []
        final_df = pd.DataFrame(columns=headers)

        # sample_size represents max_records_per_individual used
        if epsilon < 5.0:
            globals.sample_size = 10
        else:
            globals.sample_size = 30
        # sensitivity = (histograms x max_records_per_individual) + 2 population queries
        globals.sensitivity = (3 * globals.sample_size) + 2

        # Create the taxi_drivers - 1st population count
        drivers = ground_truth['taxi_id'].unique().tolist()
        num_drivers = len(drivers)
        num_drivers_noise = int(utilities.laplaceMechanism(num_drivers, globals.sensitivity, epsilon))

        # Create the three histograms
        logger.info(f"begin histogram creation {epsilon}")
        spd_pop, spd_w = utilities.set_pop_weight(ground_truth, 'shift_pca_dca', epsilon)
        cp_pop, cp_w = utilities.set_pop_weight(ground_truth, 'company_payment', epsilon)
        fr_pop, fr_w = utilities.set_pop_weight(ground_truth, 'fare_codes', epsilon)

        # Create the trips - 2nd population count
        tr_pop, tr_w = utilities.set_pop_weight_trips(ground_truth, 'taxi_id', epsilon, e_counter)
        logger.info(f"end histogram creation {epsilon}")

        # Initialize initial_driver (taxi_id) and counters
        initial_driver = 1000000
        all_counter = 0

        # Create a list of random combined features equal to max_records length
        shift_pca_dca = choices(spd_pop, spd_w, k=max_records)
        fares = choices(fr_pop, fr_w, k=max_records)
        # test = len(shift_pca_dca)

        # The driver (taxi_id) for loop
        for driver in range(initial_driver, (initial_driver + num_drivers_noise)):
            counter += 1
            if counter % 1000 == 0:
                logger.info(f"processing {counter} drivers {all_counter}")

            # Create the number of trips for a driver
            num_trips = choices(tr_pop, tr_w)[0]
            if num_trips > 200:
                num_trips = 200

            # Select random company and payment type for a driver
            company_payment = choices(cp_pop, cp_w, k=1)

            # The trip for loop
            for trip in range(num_trips):
                row, row1 = simulate_row(epsilon,
                                         driver,
                                         shift_pca_dca[all_counter],
                                         company_payment[0],
                                         fares[all_counter]
                                         )
                all_counter += 1
                # Create two lists
                #   - front_list contains epsilon, driver, spd, cp, sec_estimate
                #   - end_list contains fare, tips, trip_total, trip_seconds, trip_miles
                front_list.append(row)
                end_list.append(row1)

        # Concatenate the two list sorted by seconds estimate and trip_seconds
        logger.info("concatenation start")
        front_df = pd.DataFrame.from_dict(front_list)
        front1_df = front_df.sort_values(by=['sec_estimate'])
        front1_df = front_df.drop(columns=['sec_estimate'])
        end_df = pd.DataFrame.from_dict(end_list)
        end1_df = end_df.sort_values(by=['trip_seconds'])
        final_df = pd.concat([front1_df, end1_df], axis=1)
        logger.info("concatenation end")

        # Output to a file
        logger.info(f"writing temp file for epsilon {epsilon}")
        f_name = 'temp' + str(e_counter) + '.csv'
        epsilon_file = ROOT_DIRECTORY / f_name
        if e_counter == 1:
            final_df.to_csv(epsilon_file, index=False)
        else:
            final_df.to_csv(epsilon_file, header=False, index=False)
        e_counter += 1
        filenames.append(epsilon_file)
        logger.info(f"done for epsilon {epsilon}")

    logger.info("writing submission.csv")
    with open(output_file, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)


main()
