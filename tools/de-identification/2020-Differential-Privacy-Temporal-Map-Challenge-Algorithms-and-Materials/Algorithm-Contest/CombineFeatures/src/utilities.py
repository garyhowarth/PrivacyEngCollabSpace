# Imports
import pandas as pd
import numpy as np
# import json
from loguru import logger

import globals


# The laplaceMechanism
def laplaceMechanism(x, m, e):
    if x != 0:
        x += np.random.laplace(0, m/e, 1)[0]
    return x


# Create the weights for histograms using a sample equal to sample_size
def weight(df, c, b, e):

    temp_df = df[['taxi_id', c]]
    temp_df = temp_df.drop_duplicates()
    new_df = temp_df.groupby('taxi_id').apply(lambda x: x.sample(n=globals.sample_size, replace=True))
    new_df = new_df.reset_index(drop=True)
    new_df = new_df[c].groupby(pd.cut(new_df[c], b)).count()

    # Add noise
    for i in range(len(new_df)):
        new_df[i] = laplaceMechanism(new_df[i], globals.sensitivity, e)

    for i in range(len(new_df)):
        if new_df[i] < 0:
            new_df[i] = 0

    final_df = new_df / new_df.sum()
    w = []
    for i in range(len(final_df.index)):
        w.append(final_df[i])
    return w


# Create the raw weights for trips
def raw_weight_trips(df, c, b):

    ilist = []
    for i in range(1, 201):
        ilist.append(i)
    new_df = pd.Series(0, index=ilist)

    taxis = df[c].unique().tolist()
    t_counter = 0
    for taxi in taxis:
        trip_count = (df[c].values == taxi).sum()

        t_counter += 1
        if t_counter % 10000 == 0:
            logger.info(f"processing {t_counter} drivers for trips")
        new_df[trip_count] += 1

    return new_df


# Privatize the weights for trips
def privatize_trips(df, e):

    for i in range(1, 201):
        df[i] = laplaceMechanism(df[i], globals.sensitivity, e)

    for i in range(1, 201):
        if df[i] < 0:
            df[i] = 0

    final_df = df / df.sum()
    w = []
    for i in range(1, 201):
        w.append(final_df[i])

    return w


# Convert fare to a fare code
def convert_fare(n, d):
    if n < 1:
        return 10
    else:
        for key in d:
            if key >= n:
                return int(d[key])
                break


# Pre-process the data
def pre_process(df):

    lookup_df = pd.crosstab(df['pickup_community_area'], df['dropoff_community_area'], values=df['trip_seconds'], aggfunc='mean')
    lookup_df = lookup_df.fillna(0)
    lookup_df = lookup_df.reset_index(drop=True)
    lookup_df = lookup_df.rename(columns={-1: 0})
    globals.prox_dict = {}
    for i in range(78):
        for j in range(78):
            p_key = str(i).zfill(2)
            d_key = str(j).zfill(2)
            key = p_key + d_key
            value = int(lookup_df[j][i])
            globals.prox_dict[key] = value

    # shift_pca_dca
    df['pickup_community_area'] = df['pickup_community_area'].replace(to_replace = -1, value = 0)
    df['shift_char'] = df['shift'].astype(str).apply(lambda x: x.zfill(2))
    df['dropoff_community_area'] = df['dropoff_community_area'].replace(to_replace = -1, value = 0)
    df['pca_char'] = df['pickup_community_area'].astype(str).apply(lambda x: x.zfill(2))
    df['dca_char'] = df['dropoff_community_area'].astype(str).apply(lambda x: x.zfill(2))
    df['pca_dca'] = df['pca_char'] + df['dca_char']
    df['shift_pca_dca'] = '1' + df['shift_char'] + df['pca_char'] + df['dca_char']
    df['shift_pca_dca'] = df['shift_pca_dca'].astype(int)

    # company_payment
    df['payment_type'] = df['payment_type'].replace(to_replace=-1, value=9)
    df['company'] = df['company_id'].astype(str).apply(lambda x: x.zfill(3))
    df['payment'] = df['payment_type'].astype(str)
    df['company_payment'] = '1' + df['company'] + df['payment']
    df['company_payment'] = df['company_payment'].astype(int)

    # fare related features - fare, tips, trip_seconds, trip_miles
    fare_bins = np.r_[-np.inf, np.arange(0, 55, 5), np.inf]
    fare_pop = [i + 10 for i in range(len(fare_bins))]
    fare_pop.pop()
    fare_dict = {fare_bins[i+1]: fare_pop[i] for i in range(len(fare_pop))}
    globals.faredecode_dict = {fare_pop[i]: fare_bins[i+1] for i in range(len(fare_pop))}

    tips_bins = np.r_[-np.inf, np.arange(0, 22, 2), np.inf]
    tips_pop = [i + 10 for i in range(len(tips_bins))]
    tips_pop.pop()
    tips_dict = {tips_bins[i+1]: tips_pop[i] for i in range(len(tips_pop))}
    globals.tipsdecode_dict = {tips_pop[i]: tips_bins[i+1] for i in range(len(tips_pop))}

    sec_bins = np.r_[-np.inf, np.arange(0, 5100, 100), np.inf]
    sec_pop = [i + 10 for i in range(len(sec_bins))]
    sec_pop.pop()
    sec_dict = {sec_bins[i+1]: sec_pop[i] for i in range(len(sec_pop))}
    globals.secdecode_dict = {sec_pop[i]: sec_bins[i+1] for i in range(len(sec_pop))}

    miles_bins = np.r_[-np.inf, np.arange(0, 22, 2), np.inf]
    miles_pop = [i + 10 for i in range(len(miles_bins))]
    miles_pop.pop()
    miles_dict = {miles_bins[i+1]: miles_pop[i] for i in range(len(miles_pop))}
    globals.milesdecode_dict = {miles_pop[i]: miles_bins[i+1] for i in range(len(miles_pop))}

    df['farec'] = df['fare'].apply(convert_fare, args=[fare_dict])
    df['tipsc'] = df['tips'].apply(convert_fare, args=[tips_dict])
    df['seconds'] = df['trip_seconds'].apply(convert_fare, args=[sec_dict])
    df['miles'] = df['trip_miles'].apply(convert_fare, args=[miles_dict])

    df['fare_codes'] = df['farec'].astype(str) + \
                       df['tipsc'].astype(str) + \
                       df['seconds'].astype(str) + \
                       df['miles'].astype(str)
    df['fare_codes'] = df['fare_codes'].astype(int)

    df = df.drop(columns=['shift_char', 'pca_char', 'dca_char', 'company', 'payment', \
                          'farec', 'tipsc', 'seconds', 'miles'])

    return df


# Create the weights for the histograms
def set_pop_weight(df, c, e):

    # taxi_id histogram
    taxi_bins = df[c].unique().tolist()
    taxi_bins.append(-np.inf)
    taxi_bins.sort()

    taxi_pop = df[c].unique().tolist()
    taxi_pop.sort()

    taxi_w = weight(df, c, taxi_bins, e)

    return taxi_pop, taxi_w


# Create the weights for the trips
def set_pop_weight_trips(df, c, e, ec):

    # taxi_id histogram
    taxi_bins = [x + 1 for x in range(200)]
    taxi_bins.append(-np.inf)
    taxi_bins.sort()

    taxi_pop = [x + 1 for x in range(200)]
    taxi_pop.sort()

    if ec == 1:
        globals.taxi_rw = raw_weight_trips(df, c, taxi_bins)

    taxi_w = privatize_trips(globals.taxi_rw, e)

    return taxi_pop, taxi_w
