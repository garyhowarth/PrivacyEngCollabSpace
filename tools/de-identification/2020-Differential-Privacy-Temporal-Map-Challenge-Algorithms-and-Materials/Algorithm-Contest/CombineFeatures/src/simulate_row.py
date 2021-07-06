import random

import globals


# Create two concurrent lists representing a split row
#   - row is the front end of the row with sec_estimate faredecode_dict
#   - row1 is the back end of the row
def simulate_row(epsilon, taxi_id, spd, cp, fr):
    row = {}
    row1 = {}

    # Create row = epsilon, taxi_id, shift, company_id, pcs, dca, payment_type, sec_estimate
    row['epsilon'] = epsilon
    row['taxi_id'] = taxi_id

    row['shift'] = int(str(spd)[1:3])
    row['company_id'] = int(str(cp)[1:4])

    pca = int(str(spd)[3:5])
    if pca == 0:
        pca = -1
    row['pickup_community_area'] = pca

    dca = int(str(spd)[5:7])
    if dca == 0:
        dca = -1
    row['dropoff_community_area'] = dca

    pay = int(str(cp)[4:5])
    if pay == 9:
        pay = -1
    row['payment_type'] = pay

    pca_dca = str(spd)[3:7]
    sec_estimate = globals.prox_dict[pca_dca]
    row['sec_estimate'] = sec_estimate

    # Create row1 = fare, tips, trip_total, trip_seconds, trip_miles
    fare_range = int(str(fr)[0:2])
    tips_range = int(str(fr)[2:4])

    if fare_range == 21:
        v = 50
    else:
        v = globals.faredecode_dict[fare_range]
    if v == 0:
        value = 0
    elif v == 50:
        value = random.randrange(50, 100)
    else:
        value = random.randrange(v - 5, v)
    row1['fare'] = value
    fare = value

    if tips_range == 21:
        v = 20
    else:
        v = globals.tipsdecode_dict[tips_range]
    if v == 0:
        value = 0
    elif v == 20:
        value = random.randrange(20, 50)
    else:
        value = random.randrange(v - 2, v)
    row1['tips'] = value
    tips = value

    row1['trip_total'] = fare + tips

    sec_range = int(str(fr)[4:6])
    miles_range = int(str(fr)[6:8])

    if sec_range == 61:
        v = 5000
    else:
        v = globals.secdecode_dict[sec_range]
    if v == 0:
        value = 0
    elif v == 5000:
        value = random.randrange(5000, 10000)
    else:
        value = random.randrange(v - 100, v)
    row1['trip_seconds'] = value

    if miles_range == 21:
        v = 20
    else:
        v = globals.milesdecode_dict[miles_range]
    if v == 0:
        value = 0
    elif v == 20:
        value = random.randrange(20, 50)
    else:
        value = random.randrange(v - 2, v)
    row1['trip_miles'] = value

    return row, row1
