from BaconShorSamplers import *
import numpy as np
from datetime import datetime
# import argparse
import sys
import math

sampler_dict = {
    "initialization errors": initialization_error_sampler,
    "code capacity": code_capacity_sampler,
    "measurement errors": measurement_error_sampler
}

def progress_bar(pct):
    sys.stdout.write('\r')
    sys.stdout.write(f'[{"="*math.ceil(pct*20):20s}] {pct:%}')
    sys.stdout.flush()

def monte_carlo_simulator(mode, min_error_rate, max_error_rate, x_tick_number, req_samples):
    physical_error_rates = np.linspace(min_error_rate, max_error_rate, x_tick_number)
    no_errors = np.zeros(x_tick_number, np.uint32)
    undetected_errors = np.zeros(x_tick_number, np.uint32)
    uncorrected_errors = np.zeros(x_tick_number, np.uint32)
    corrected_errors = np.zeros(x_tick_number, np.uint32)
    sampler = sampler_dict[mode]

    for i in range(x_tick_number):
        now = datetime.now()
        print(f'{now.strftime("%Y-%m-%d, %H:%M:%S")} Physical error rate {physical_error_rates[i]:.2e}')
        while uncorrected_errors[i] < req_samples:
            result = sampler(physical_error_rates[i])
            if result == "No Error":
                no_errors[i] += 1
            if result == "Undetected Error":
                undetected_errors[i] += 1
            if result == "Corrected Error":
                corrected_errors[i] += 1
            if result == "Uncorrected Error":
                uncorrected_errors[i] += 1
                progress_bar(float(uncorrected_errors[i])/req_samples)
    data = np.vstack((physical_error_rates, no_errors, undetected_errors, uncorrected_errors, corrected_errors))
    return data

def save_data(data, filename):    
    data = np.transpose(data)
    np.savetxt(filename, data, delimiter = ",")

def load_data(filename):
    data = np.loadtxt(filename, delimiter =",")
    data = np.transpose(data)
    return data

def pseudo_threshold_plot(data, time, mode):
    pass

def proportion_plot(data, time, mode):
    pass

def main():
    # need to implement arg parser

    mode =  "code_capacity"
    min_error_rate = 1e-4
    max_error_rate = 1e-2
    x_tick_number = 100
    req_samples = 100

    data = monte_carlo_simulator(mode, min_error_rate, max_error_rate, x_tick_number, req_samples)

    time_str = datetime.now().strftime("%m%d_%H%M")
    path = "simulation results/"
    fname = f"{path}{time_str}_{mode}_{min_error_rate:0.2e}_{max_error_rate:0.2e}_{x_tick_number}_{req_samples}"

    save_data(data, fname)

    #data = load_data(fname)

    pseudo_threhsold = pseudo_threshold_plot(data, time_str, mode)
    proportion_plot(data, time_str, mode)

    print(f"The pseudo-threshold is {pseudo_threhsold}")



  

# parser = argparse.ArgumentParser()
# parser.add_argument('-t', metavar='test', type=int, default=None, help='test cases', choices=range(1, 16))
# parser.add_argument('-d', metavar='debug', type=int, default=0, help='debug', choices=range(0, 2))
# args = parser.parse_args()


if __name__ == "__main__":
    main()
