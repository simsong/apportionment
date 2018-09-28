#!/usr/bin/env python

"""
Noisy apportion: See how differential privacy changes apportionment.
"""

from apportion import get_populations,apportion,print_seats

import csv
import math
import sys
import json
import numpy as np
from multiprocessing import Pool, TimeoutError

INF                = float('inf')
BASE_POPULATIONS   = get_populations()
BASE_APPORTIONMENT = apportion(BASE_POPULATIONS)
NUMBER_STATES    = 50
EPSILONS         = "0.00001,0.00005,0.0001,0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.001,.002,.003,.004,.005,0.01,0.05,0.1,0.5,1.0"

assert len(BASE_POPULATIONS) == NUMBER_STATES
assert "Virginia" in BASE_POPULATIONS
assert "Puerto Rico" not in BASE_POPULATIONS

def noisy_population(epsilon,debug=False):
    """Return the populations, with laplace noise added"""
    populations = {}
    noise = np.random.laplace(loc = 0, scale = 1.0/epsilon, size = (1, len(BASE_POPULATIONS)))
    for (count,(state,pop)) in enumerate(BASE_POPULATIONS.items()):
        populations[state] = int(round(pop + noise[0,count]))
        if debug:
            print("{}: {} + {} = {}".format(state,pop, noise[0,count], populations[state]))
    if debug:
        print("-------------------------------")
    return populations
    
def L1_error(a,b):
    if a==b: 
        return 0
    return sum([abs(a[k]-b[k]) for k in a.keys()])

def error_for_epsilon(epsilon,debug=False):
    noisy_populations   = noisy_population(epsilon=epsilon,debug=False)
    noisy_apportionment = apportion(noisy_populations)
    return L1_error(BASE_APPORTIONMENT, noisy_apportionment)
    
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-e", "--epsilons", help="Specify a set of epsilons", default=EPSILONS)
    parser.add_argument("-t", "--trials", help="Number of trials at each epsilon", default=100, type=int)
    parser.add_argument("-j", "--threads", help="Number of threads", default=1, type=int)
    
    args = parser.parse_args()

    pool = Pool(args.threads) if args.threads>1 else None

    print(f"Trials per epsilon: {args.trials}")
    print("Epsilon    Errors       Max Error")
    for epsilon in [float(f) for f in args.epsilons.split(",")]:
        epsilons = [epsilon] * args.trials
        if pool:
            errors = pool.map( error_for_epsilon, epsilons ) 
        else:
            errors = [error_for_epsilon(epsilon) for epsilon in epsilons]
        print("{:1.5f}  errors: {}   max error: {}".format(epsilon, np.count_nonzero(errors), max(errors)))

