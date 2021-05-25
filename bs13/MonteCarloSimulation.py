from BaconShorSamplers import *
import numpy as np

sampler_dict = {
    "initialization errors": initialization_error_sampler,
    "code capacity": code_capacity_sampler,
    "measurement errors": measurement_error_sampler
}

def monte_carlo_simulator(mode, min_error_rate, max_error_rate, x_tick_number, req_samples):
    physical_error_rates = np.linspace(min_error_rate, max_error_rate, x_tick_number)
    no_errors = np.zeros(x_tick_number)
    undetected_errors = np.zeros(x_tick_number)
    uncorrected_errors = np.zeros(x_tick_number)
    corrected_errors = np.zeros(x_tick_number)
    sampler = sampler_dict[mode]

    for i in range(x_tick_number):
        while uncorrected_errors[i] < req_samples:
            result = sampler(physical_error_rates[i])
            if "No Error":
                no_errors[i] += 1
            if "Undetect Error":
                undetected_errors[i] += 1
            if "Corrected Error":
                corrected_errors[i] += 1
            if "Uncorrected Error":
                uncorrected_errors[i] += 1

    return physical_error_rates, no_errors, undetected_errors, corrected_errors, uncorrected_errors

def 