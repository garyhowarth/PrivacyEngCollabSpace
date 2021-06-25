# Global variables used to improve speed
#     _pop - lists with the feature population
#     _w - lists with the weights for the population
#     _dict - dictionaries for decoding combined fare features
# Combined features are:
#    - spd (shift, pickup_community_area, dropoff_community_area)
#    - cp (company, payment_type)
#    - fare (fare, tips, trip_seconds, trip_miles)
# Global sample_size variable (# taxi_ids)
# Global sensitity variable
global spd_pop, spd_w, \
       cp_pop, cp_w, \
       fare_pop, fare_w, \
       faredecode_dict, \
       tipsdecode_dict, \
       secdecode_dict, \
       milesdecode_dict, \
       prox_dict, \
       sample_size, \
       sensitivity, \
       taxi_rw
