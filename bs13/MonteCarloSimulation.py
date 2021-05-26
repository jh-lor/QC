from BaconShorSamplers import *
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
# import argparse
import sys
import math

sampler_dict = {
    "initialization_error": initialization_error_sampler,
    "code_capacity": code_capacity_sampler,
    "measurement_error": measurement_error_sampler
}

def progress_bar(pct):
    sys.stdout.write('\r')
    sys.stdout.write(f'[{"="*math.ceil(pct*20):20s}] {pct:.1%}')
    if pct == 1:
        sys.stdout.write('\n')
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
    
    expected_logical_dict = {
        "code_capacity": 1,
        "initialization_error": 2/3,
        "measurement_error": 2/3
    }

    physical_error_rates, no_errors, undetected_errors, uncorrected_errors, corrected_errors = data
    total_repetitions = no_errors + undetected_errors + uncorrected_errors + corrected_errors
    fig, ax = plt.subplots()

    simulation_logical_error_rate = (undetected_errors + uncorrected_errors)/total_repetitions
    
    proportions = [simulation_logical_error_rate*100]
    labels = ["Simulation Logical Error Rate"]
    ax.stackplot(physical_error_rates*100, proportions,
                labels = labels)
    
    expected_logical_error_rate = physical_error_rates*expected_logical_dict[mode]
    ax.plot(physical_error_rates*100, physical_error_rates*expected_logical_dict[mode]*100, label = f"Logical Error Rate for one qubit: y = {expected_logical_dict[mode]:0.2f}x")
    
    ax.legend(loc = 'upper left')
    ax.set_title(f'Logical Error Rate {mode}')
    # plt.xticks(np.arange(100*min(physical_error_rate), 100*max(physical_error_rate)+1, 5))
    ax.set_xlabel('Physical Error Rate')
    ax.set_ylabel('Logical Error Rate')
    fig.savefig(f'{plots_path}Logical Error Rate Plot {mode}_{time}.png')

    diff_list = simulation_logical_error_rate - expected_logical_error_rate
    for i in range(len(diff_list)-2):
        if diff_list[i]*diff_list[i+1] < 0:
            return (physical_error_rates[i]+physical_error_rates[i+1])/2


def proportion_plot(data, time, mode):
    fig, ax = plt.subplots()

    physical_error_rates, no_errors, undetected_errors, uncorrected_errors, corrected_errors = data

    proportions = [no_errors, corrected_errors, undetected_errors, uncorrected_errors]

    labels = [
        "No Error",
        "Error Corrected",
        "Undetected Logical Error",
        "Uncorrected Logical Error"
        ]
    ax.stackplot(physical_error_rates*100, proportions,
                labels= labels)
    ax.legend(loc='upper left')
    ax.set_title(f'Proportion {mode}')
    ax.set_xlabel('Physical Error Rate')
    ax.set_ylabel('Proportion')
    # plt.xticks(np.arange(100*min(physical_error_rate), 100*max(physical_error_rate)+1, 5))

    # ax.set_xlim(0, 20)
    # ax.set_ylim(0, 50)

    fig.savefig(f"{plots_path}Proportion of Results {mode}_{time}.png")

def main():
    # need to implement arg parser

    mode =  "code_capacity"
    min_error_rate = 0.01
    max_error_rate = 0.21
    x_tick_number = 10
    req_samples = 100

    data = monte_carlo_simulator(mode, min_error_rate, max_error_rate, x_tick_number, req_samples)

    time_str = datetime.now().strftime("%m%d_%H%M")
    path = "./simulation results/"
    fname = f"{path}{time_str}_{mode}_{min_error_rate:0.2e}_{max_error_rate:0.2e}_{x_tick_number}_{req_samples}"

    save_data(data, fname)

    #data = load_data(fname)

    pseudo_threhsold = pseudo_threshold_plot(data, time_str, mode)
    proportion_plot(data, time_str, mode)

    print(f"The pseudo-threshold is {pseudo_threhsold:0.2e}")



  

# parser = argparse.ArgumentParser()
# parser.add_argument('-t', metavar='test', type=int, default=None, help='test cases', choices=range(1, 16))
# parser.add_argument('-d', metavar='debug', type=int, default=0, help='debug', choices=range(0, 2))
# args = parser.parse_args()

plots_path = "./plots/"
if __name__ == "__main__":
    main()
