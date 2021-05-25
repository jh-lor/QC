from BaconShor import BaconShor13

def check_X_logical_error(state):
    return True if sum(state[:9,0])%2 else False

def check_both_logical_error(state):
    return True if sum(state[:9,0])%2 or sum(state[:9,1])%2 else False

def initialization_error_sampler(physical_error_rate):
    bs13 = BaconShor13(physical_error_rate)
    bs13.initialize_FT()
    measurements = bs13.measure_syndrome()

    if any(measurements.values()):
        bs13.correctError()
        bs13.measure_syndrome()
        if check_X_logical_error(bs13.sim.state):
            return "Uncorrected Error"
        else:
            return "Corrected Error"
    else:
        if check_X_logical_error(bs13.sim.state):
            return "Undetected Error"
        else:
            return "No Error"

def code_capacity_sampler(physical_error_rate):
    bs13 = BaconShor13(physical_error_rate)
    bs13.single_qubit_errors()
    measurements = bs13.measure_syndrome()

    if any(measurements.values()):
        bs13.correctError()
        bs13.measure_syndrome()
        if check_both_logical_error(bs13.sim.state):
            return "Uncorrected Error"
        else:
            return "Corrected Error"
    else:
        if check_both_logical_error(bs13.sim.state):
            return "Undetected Error"
        else:
            return "No Error"

def measurement_error_sampler(physical_error_rate):
    bs13 = BaconShor13(physical_error_rate)
    bs13.initialize_FT()

    #state 1: repeat syndrome measurement with errors until an error is detected
    while not any(bs13.measure_syndrome(True).values()):
        continue
    
    #state 2: repeat syndrome measurement with errors once and correct errors
    bs13.measure_syndrome(True)
    bs13.correctError()

    #state 3: run syndrome measurement perfectly and correct error to check logical error
    bs13.measure_syndrome()
    bs13.correctError()
    bs13.execute()

    if check_X_logical_error(bs13.sim.state):
        return "Uncorrected Error"
    else:
        return "Corrected Error"
