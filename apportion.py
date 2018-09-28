#!/usr/bin/env python

import csv
import math
import sys
import json

POPULATIONS_CSV='2010.csv'
TOTAL_SEATS = 435

def get_populations(fname=POPULATIONS_CSV):
    populations = {}
    with open( fname, 'r') as f:
        for row in csv.reader(f):
            if row[0][0]=='#':
                continue
            populations[row[0]] = int(row[1])
    return populations

def apportion(populations,verbose=False):
    # First give each state one seat
    seats = dict((k,1) for (k,v) in populations.items())
    seat_count = len(seats)

    # Then allocate seats using the method of equal proportions
    while seat_count < TOTAL_SEATS:
        (max_priority, max_state) = (0, '')
        for (state, pop) in populations.items():
            n = seats[state]
            A = pop / math.sqrt(n*(n+1))
            if (A > max_priority):
                (max_priority, max_state) = (A, state)
        seat_count += 1
        seats[max_state] +=1
        if verbose:
            print("house seat: %s, priority: %.0f, state: %s, state seats: %s"
                  % (seat_count, max_priority, max_state, seats[max_state]))
    return seats

def print_seats(seats):
    # Show results
    fmt0="{:<15} {:>5} {:>5} {:>5}  {:>5} {:>10}"
    fmt1="{:<15} {:>5} {:>5}  {:6.2f} {:>5} {:>10}"
    print(fmt0.format("State","Seats","⌊quota⌋","quota","⌈quota⌉","people per seat"))
    for k in sorted(seats.keys()):
        quota = TOTAL_SEATS*populations[k]*1.0/total_population
        print(fmt1.format(k, seats[k], 
                         int(math.floor(quota)), quota, int(math.ceil(quota)), int(populations[k]/seats[k])))

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-s", "--save", help="Save apportionment into a JSON file")
    args = parser.parse_args()

    populations = get_populations( POPULATIONS_CSV )
    total_population = sum(v for v in populations.values())
    print("total population: ",total_population)
    seats = apportion(populations, verbose=True)
    print_seats(seats)

    if args.save:
        with open(args.save, "w") as f:
            json.dump( seats, f )
        
