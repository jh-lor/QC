from PauliSim import PauliSim
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import sys

class BaconShor13():
    """Implements a Bacon-Shor-13 simulation using the PauliSim class
    """
    def __init__(self, mode, p = 0, state = None):
        """Initializes BaconShor object with error mode, physical error and initial state

        Args:
            mode (str): error mode for simulation
            p (float, optional): physical error rate. Defaults to 0.
            state (numpy arr (int), optional): initial state of system. Defaults to None.
        """
        self.errorRate = p
        self.measurements = {}
        self.appliedchannels = []
        self.mode = mode

        if not state:
            self.state = np.array(np.zeros(2*13).reshape(13,2), dtype = bool)
        else:
            self.state = state.astype(bool)

        self.mode_dict = {
            "default":
                {
                    "initialization": True,
                    "measurement": False,
                    "one_qubit": False
                },
            "initialization_errors":
                {
                    "initialization": True,
                    "measurement": False,
                    "one_qubit": False
                },
            "code_capacity":
                {
                    "initialization": False,
                    "measurement": False,
                    "one_qubit": True
                },
            "measurement_error":
                {
                    "initialization": True,
                    "measurement": True,
                    "one_qubit": False
                }
        }

    def initialize(self, Xerr = [], Zerr = []):
        """Intializes the Bacon-Shor-13 circuit and measures the stabilizers

        Args:
            Xerr (list, optional): list of index of qubits to append X gates to before stabilizers. For debugging purposes. Defaults to [].
            Zerr (list, optional): list of index of qubits to append Z gates to before stabilizers. For debugging purposes. Defaults to [].

        Returns:
            dict: dictionary of measurements. Keys are the stabilizer names.
        """
        sim = PauliSim(13)
        sim.addTag("Initialization")
        if self.mode_dict[self.mode]["initialization"]:
            sim.addCNOT(0,3) 
            sim.addCNOT(0,6)  

            for i in [0,3,6]:
                sim.addH(i)

            sim.addCNOT(0,1)
            sim.addDepolarizingNoise([0,1], self.errorRate, 2)
            sim.addCNOT(0,2)
            sim.addDepolarizingNoise([0,2], self.errorRate, 2)

            sim.addCNOT(3,4)
            sim.addDepolarizingNoise([3,4], self.errorRate, 2)
            sim.addCNOT(3,5)
            sim.addDepolarizingNoise([3,5], self.errorRate, 2)

            sim.addCNOT(6,7)
            sim.addDepolarizingNoise([6,7], self.errorRate, 2)
            sim.addCNOT(6,8)
            sim.addDepolarizingNoise([6,8], self.errorRate, 2)

            for i in range(0,9):
                sim.addH(i)

        for qubit in Xerr:
            sim.addX(qubit)
        
        for qubit in Zerr:
            sim.addZ(qubit)

        # Assume perfect initialization
        if self.mode_dict[self.mode]["one_qubit"]:
            for i in range(9):
                sim.addDepolarizingNoise(i, self.errorRate, 1)

        return self.measure_syndrome(sim, error = self.mode_dict[self.mode]["measurement"])

    def correctError(self, error = False):
        """Measures stabilizers, decode error string and appends the appropriate gate. Measurement may have errors

        Args:
            error (bool, optional): whether measurement errors can occur. Defaults to False.

        Returns:
            dict: dictionary of measurements. Keys are the stabilizer names.
        """
        
        lookup_table = {
        '0000': 'IIIIIIIII',
        '0100': 'IIZIIIIII',
        '1000': 'ZIIIIIIII',
        '1100': 'IZIIIIIII',
        '0010': 'XIIIIIIII',
        '0001': 'IIIIIIXII',
        '0011': 'IIIXIIIII',
        '1010': 'YIIIIIIII',
        '1011': 'IIIYIIIII',
        '1001': 'IIIIIIYII',
        '1110': 'IYIIIIIII',
        '1111': 'IIIIYIIII',
        '1101': 'IIIIIIIYI',
        '0110': 'IIYIIIIII',
        '0111': 'IIIIIYIII',
        '0101': 'IIIIIIIIY'
        }

        error_string =  ""
        error_string += str(self.measurements["X1X2X4X5X7X8"])
        error_string += str(self.measurements["X2X3X5X6X8X9"])
        error_string += str(self.measurements["Z1Z4Z2Z5Z3Z6"])
        error_string += str(self.measurements["Z4Z7Z5Z8Z6Z9"]) 
        
        decode_string = lookup_table.get(error_string)
 
        #initialize 9 data qubits, 5 error qubits
        for i in [9, 10, 11, 12]:
            self.state[i][0] = 0
        sim = PauliSim(13, self.state)
        sim.addTag("Error Correction")

        for i in range(len(decode_string)):
            if decode_string[i] != 'I':
                if decode_string[i] =='X': 
                    sim.addX(i)
                if decode_string[i] =='Y': 
                    sim.addY(i)
                if decode_string[i] =='Z': 
                    sim.addZ(i)

        return self.measure_syndrome(sim = sim, error = error)
    
    def measure_syndrome(self, sim = None, initial_state = None, error = False):
        """Appends stabilizers and measure the stabilizers

        Args:
            sim (PauliSim, optional): existing pauli simulators whose stabilizer is measured. Defaults to None.
            initial_state (numpy arr(int), optional): state to measure stabilizers of. Defaults to None.
            error (bool, optional): whether there is measurement error. Defaults to False.

        Returns:
            dict: dictionary of measurements. Keys are the stabilizer names.
        """
        
        if not sim:
            sim = PauliSim(initial_state = initial_state)

        sim.addTag("Measure Syndrome")

        if error:
            sim.addZStabilizer([0,3,1,4,2,5], 9, self.errorRate)
            sim.addZStabilizer([3,6,4,7,5,8], 10, self.errorRate)
            sim.addXStabilizer([0,1,3,4,6,7], 11, self.errorRate)
            sim.addXStabilizer([1,2,4,5,7,8], 12, self.errorRate)
        else:
            sim.addZStabilizer([0,3,1,4,2,5], 9)
            sim.addZStabilizer([3,6,4,7,5,8], 10)
            sim.addXStabilizer([0,1,3,4,6,7], 11)
            sim.addXStabilizer([1,2,4,5,7,8], 12)

        sim.addMeasurement(11, "X1X2X4X5X7X8")
        sim.addMeasurement(12, "X2X3X5X6X8X9")
        sim.addMeasurement(9, "Z1Z4Z2Z5Z3Z6")        
        sim.addMeasurement(10, "Z4Z7Z5Z8Z6Z9")

        # reset ancilla
        for i in [9, 10, 11 ,12]:
            sim.addReset(i)

        self.state = sim.execute()
        self.appliedchannels += sim.getOperations()
        self.measurements = sim.measurements

        return self.measurements

def SimulateEncoding(min_error_rate, max_error_rate, samples, repetitions, mode):
    """Monte Carlo simulation of encoding under the code capacity or initialization error model.

    Args:
        min_error_rate (float): minimum physical error rate of simulation
        max_error_rate (float): maximum physical error rate of simulation
        samples (int): number of physical error rate values to simulate
        repetitions (int): number of simulations per physical error rate
        mode (str): error model to use

    Returns:
        x_array (numpy arr (int)): physical error rate values simulated
        no_error (numpy arr (int)): number of simulations with no logical error
        error_detected (numpy arr (int)): number of simulations with an error detected
        error_not_detected (numpy arr (int)): number of simulations with a logical error but it is not detected
        error_corrected (numpy arr (int)): number of simulations with an error that is corrected
        error_not_corrected (numpy arr (int)): number of simuations with an error that is incorrectly corrected
    """
    x_array = np.linspace(min_error_rate, max_error_rate, samples)

    no_error = np.zeros(samples,dtype = np.uint32)

    error_detected = np.zeros(samples, dtype = np.uint32)
    error_not_detected = np.zeros(samples, dtype = np.uint32)

    error_corrected = np.zeros(samples, dtype = np.uint32)
    error_not_corrected= np.zeros(samples, dtype = np.uint32)
    
    def LogicalError(state):
        both_errors = ["code_capacity"]
        if mode in both_errors:
            return True if sum(state[:,0]) % 2 or sum(state[:,1])%2 else False # checks both X and Z errors
        return True if sum(state[:,0])%2 else False # only checks X errors

    for i in range(len(x_array)):
        now = dt.datetime.now()
        print(f'{now.strftime("%Y-%m-%d, %H:%M:%S")} Physical error rate {x_array[i]:.2e}')
        for j in range(repetitions):
            bs13 = BaconShor13(p = x_array[i], mode = mode)
            before_correction = bs13.initialize()
            if before_correction["X1X2X4X5X7X8"] or before_correction["X2X3X5X6X8X9"] or before_correction["Z1Z4Z2Z5Z3Z6"] or before_correction["Z4Z7Z5Z8Z6Z9"]:
                error_detected[i] += 1 
                bs13.correctError()
                # check the parity of the x bits and the z bits - even parity for both means no errors
                if LogicalError(bs13.state):
                    error_not_corrected[i] += 1
                else:
                    error_corrected[i] += 1
            else:
                if LogicalError(bs13.state):
                    error_not_detected[i] +=1
                else:
                    no_error[i] += 1
            if j<10:
                print(bs13.state)
                print(bs13.appliedchannels)

    return x_array, no_error, error_detected, error_not_detected, error_corrected, error_not_corrected

def SimulateMeasurementError(min_error_rate, max_error_rate, samples, req_count, mode = "measurement_error"):
    """Monte Carlo simulation of Bacon-Shor-13 encoding with measurement error(repeat measurement until error is detected and then measure again)

    Args:
        min_error_rate (float): minimum physical error rate of simulation
        max_error_rate (float): maximum physical error rate of simulation
        samples (int): number of physical error rate values to simulate
        repetitions (int): number of simulations per physical error rate
        mode (str): error model to use (measurement_error)

    Returns:
        x_array (numpy arr (int)): physical error rate values simulated
        no_error (numpy arr (int)): number of simulations with no logical error
        logical_error (numpy arr (int)): number of simultaions with logical error
    """
    x_array = np.linspace(min_error_rate, max_error_rate, samples)

    no_error = np.zeros(samples,dtype = np.uint32)
    logical_error = np.zeros(samples, dtype = np.uint32)

    def LogicalError(bs13):
        bs13.correctError(False)
        return True if sum(bs13.state[:,0])%2 else False # only checks X errors

    for i in range(len(x_array)):
        now = dt.datetime.now()
        print(f'{now.strftime("%Y-%m-%d, %H:%M:%S")} Physical error rate {x_array[i]:.2e}')
        while logical_error[i] < req_count:
            bs13 = BaconShor13(p = x_array[i], mode = mode)
            measurement_dict = bs13.initialize()

            while not(measurement_dict["X1X2X4X5X7X8"] or measurement_dict["X2X3X5X6X8X9"] or measurement_dict["Z1Z4Z2Z5Z3Z6"] or measurement_dict["Z4Z7Z5Z8Z6Z9"]):
                # 0000 - repeat measurement
                measurement_dict = bs13.measure_syndrome(initial_state = bs13.state, error = True)
            # found an error - correct it
            # second state
            bs13.correctError(True)

            if LogicalError(bs13):
                error_list = [operation for operation in bs13.appliedchannels if "err" in operation]

                print(error_list)
                break
                logical_error[i] +=1
                
            else: 
                no_error[i] += 1
    return x_array, no_error, logical_error

def v1():#repetitons, x_tick_number, min_error_rate, max_error_rate, mode):
    """Runs monte-carlo simulation for specified parameters and saves results and plots logical error rate against physical error rate
    """
    # Generate Data
    repetitions = 5000
    x_tick_number = 20
    min_error_rate = 0
    max_error_rate = 1
    mode = "initialization_errors"
    # mode = "code_capacity"
    results_path = "./simulation results/"
        
    physical_error_rate, no_error, error_detected, error_not_detected, error_corrected, error_not_corrected = SimulateEncoding(min_error_rate, max_error_rate, x_tick_number, repetitions, mode)
    data = np.vstack((physical_error_rate, no_error, error_detected, error_not_detected, error_corrected, error_not_corrected))
    data = np.transpose(data)
    np.savetxt(f"{results_path}simulation_data_{repetitions}_{x_tick_number}_{min_error_rate}_{max_error_rate}_{mode}.csv", data, delimiter = ",")


    # Load Data
    # data = np.loadtxt(f"{results_path}simulation_data_{repetitions}_{x_tick_number}_{min_error_rate}_{max_error_rate}_{mode}.csv", delimiter =",")
    # data = np.transpose(data)

    # physical_error_rate = data[0]
    # no_error = data[1].astype(np.uint32)
    # error_detected = data[2].astype(np.uint32)
    # error_not_detected = data[3].astype(np.uint32)
    # error_corrected = data[4].astype(np.uint32)
    # error_not_corrected = data[5].astype(np.uint32)


    # plot error statistics before correction
    error_before_detection = error_not_detected + error_detected
    no_error_rate = no_error*(100/repetitions)
    failed_detection_rate = error_not_detected*(100/repetitions)
    error_detection_rate = error_detected*(100/repetitions)

    # plot error statistics after correction
    total_error_corrected_rate = error_corrected*(100/repetitions)
    total_error_not_corrected_rate = error_not_corrected*(100/repetitions)

    # plot error statistics of correction
    no_zeros = np.where(error_detected == 0, 1, error_detected)
    error_corrected_rate = error_corrected/no_zeros * 100
    error_not_corrected_rate = error_not_corrected/no_zeros * 100

    plots_path = "./plots/"
    fig, ax = plt.subplots()
    expected_logical_error_rate = 2/3*100
    if mode == "code_capacity":
        expected_logical_error_rate = 100
    proportions = [failed_detection_rate+ total_error_not_corrected_rate]
    labels = [
        "Total Logical Error Rate"
        ]
    ax.stackplot(physical_error_rate*100, proportions,
                labels= labels)
    
    ax.plot(physical_error_rate*100,physical_error_rate*expected_logical_error_rate, label = f"Logical Error Rate for one qubit: y = {round(expected_logical_error_rate/100,2)}x")
    ax.legend(loc = 'upper left')
    ax.set_title(f'Logical Error Rate {mode}')
    plt.xticks(np.arange(100*min(physical_error_rate), 100*max(physical_error_rate)+1, 5))
    ax.set_xlabel('Physical Error Rate')
    ax.set_ylabel('Logical Error Rate')
    # ax.set_xlim(0, 20)
    # ax.set_ylim(0, 40)

    fig.savefig(f"{plots_path}Logical Error Rate Plot {mode}_test.png")

    # expected_logical_error_rate_arr = physical_error_rate*expected_logical_error_rate/100
    # print(mode)
    # for i in range(len(physical_error_rate)):
    #     if (expected_logical_error_rate_arr[i] - proportions[0][i]/100)*(expected_logical_error_rate_arr[i-1] - proportions[0][i-1]/100)<0:
    #         print(expected_logical_error_rate_arr[i])
    #         print(proportions[0][i]/100)
    #         print(f"between {physical_error_rate[i]} and {physical_error_rate[i-1]}")

    # fig, ax = plt.subplots()
    # proportions = [no_error_rate, total_error_corrected_rate, failed_detection_rate, total_error_not_corrected_rate]

    # labels = [
    #     "No Error",
    #     "Error Corrected",
    #     "Undetected Logical Error",
    #     "Uncorrected Logical Error"
    #     ]
    # ax.stackplot(physical_error_rate*100, proportions,
    #             labels= labels)
    # ax.legend(loc='upper left')
    # ax.set_title(f'Proportion {mode}')
    # ax.set_xlabel('Physical Error Rate')
    # ax.set_ylabel('Proportion')
    # plt.xticks(np.arange(100*min(physical_error_rate), 100*max(physical_error_rate)+1, 5))

    # # ax.set_xlim(0, 20)
    # # ax.set_ylim(0, 50)

    # fig.savefig(f"{plots_path}Proportion of Results {mode}.png")

def v2():
    """Runs Monte Carlo simulation and saves results
    """
    # repetitions = 10000000
    req_counts = 100
    x_tick_number = 1
    min_error_rate = 5e-4
    max_error_rate = 5.5e-4
    results_path = "./simulation results/"
    mode = "measurement_error"

    physical_error_rate, no_error, logical_error = SimulateMeasurementError(min_error_rate, max_error_rate, x_tick_number, req_counts, mode)

    data = np.vstack((physical_error_rate, no_error, logical_error))
    data = np.transpose(data)
    
    np.savetxt(f"{results_path}simulation_data_{repetitions}_{x_tick_number}_{min_error_rate}_{max_error_rate}_{mode}.csv", data, delimiter = ",")


    # data = np.loadtxt(f"{results_path}simulation_data_{repetitions}_{x_tick_number}_{min_error_rate}_{max_error_rate}_{mode}.csv", delimiter = ",")
    # data = np.transpose(data)

    # physical_error_rate = data[0]
    # no_error = data[1].astype(np.uint32)
    # logical_error = data[2].astype(np.uint32)

    # now = dt.datetime.now()
    plots_path = "./plots/"
    fig, ax = plt.subplots()
    expected_logical_error_rate = 2/3*100
    labels = [
        "Logical Error Rate"
        ]
    ax.stackplot(physical_error_rate*100, logical_error/repetitions*100,
                labels= labels)
    ax.plot(physical_error_rate*100,physical_error_rate*expected_logical_error_rate, label = f"Logical Error Rate for one qubit: y = {round(expected_logical_error_rate/100,2)}x")
    ax.legend(loc='upper left')
    ax.set_title(f'Logical Error Rate {mode}')
    plt.xticks(np.arange(100*min(physical_error_rate), 100*max(physical_error_rate)+1, 5))
    ax.set_xlabel('Physical Error Rate')
    ax.set_ylabel('Logical Error Rate')
    # ax.set_xlim(0, 20)
    # ax.set_ylim(0, 40)

    fig.savefig(f"{plots_path}Logical Error Rate Plot {mode}.png")

    # expected_logical_error_rate_arr = physical_error_rate*expected_logical_error_rate/100
    # print(mode)
    # for i in range(len(physical_error_rate)):
    #     if (expected_logical_error_rate_arr[i] - proportions[0][i]/100)*(expected_logical_error_rate_arr[i-1] - proportions[0][i-1]/100)<0:
    #         print(expected_logical_error_rate_arr[i])
    #         print(proportions[0][i]/100)
    #         print(f"between {physical_error_rate[i]} and {physical_error_rate[i-1]}")


def simple_error_debugger():

    def LogicalError(state):
        return True if sum(state[:,0]) % 2 else False # checks X error

    for i in range(9):
        for j in range(9):
            bs13 = BaconShor13("default")
            before_correction = bs13.initialize([i],[j])
            bs13.correctError()
            print("Before Correction:")
            print(before_correction)
            print("Logical Error")
            logic_error = LogicalError(bs13.state)
            print(logic_error)
            if logic_error:
                print(bs13.state)


if __name__ == "__main__":
    v1()
