from PauliSim import PauliSim
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

class BaconShor13():
    def __init__(self, p = 0, state = None):
        self.errorRate = p
        self.measurements = {}
        self.appliedchannels = []

        if not state:
            self.state = np.array(np.zeros(2*13).reshape(13,2), dtype = bool)
        else:
            self.state = state.astype(bool)

    def initialize(self, Xerr = [], Zerr = []):

        sim = PauliSim(13)
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
        
        # for debugging 
        # for i in Xerr:
        #     sim.addX(i)
        
        # for i in Zerr:
        #     sim.addZ(i)

        sim.addZStabilizer([0,3,1,4,2,5], 9)
        sim.addZStabilizer([3,6,4,7,5,8], 10)
        sim.addXStabilizer([0,1,3,4,6,7], 11)
        sim.addXStabilizer([1,2,4,5,7,8], 12)

        self.state = sim.execute()        

        self.measurements["X1X2X4X5X7X8"] = self.state[11][0]
        self.measurements["X2X3X5X6X8X9"] = self.state[12][0]
        self.measurements["Z1Z4Z2Z5Z3Z6"] = self.state[9][0]
        self.measurements["Z4Z7Z5Z8Z6Z9"] = self.state[10][0]
        
        self.appliedchannels+= sim.getOperations()

        return self.measurements

    def correctError(self):

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

        for i in range(len(decode_string)):
            if decode_string[i] != 'I':
                if decode_string[i] =='X': 
                    sim.addX(i)
                if decode_string[i] =='Y': 
                    sim.addY(i)
                if decode_string[i] =='Z': 
                    sim.addZ(i)
      
        sim.addZStabilizer([0,3,1,4,2,5], 9)
        sim.addZStabilizer([3,6,4,7,5,8], 10)
        sim.addXStabilizer([0,1,3,4,6,7], 11)
        sim.addXStabilizer([1,2,4,5,7,8], 12)

        self.state = sim.execute()        
        self.measurements["Corrected X1X2X4X5X7X8"] = self.state[11][0]
        self.measurements["Corrected X2X3X5X6X8X9"] = self.state[12][0]
        self.measurements["Corrected Z1Z4Z2Z5Z3Z6"] = self.state[9][0]
        self.measurements["Corrected Z4Z7Z5Z8Z6Z9"] = self.state[10][0]     

        self.appliedchannels += sim.getOperations()

        return self.measurements

def SimulateEncoding(min_error_rate, max_error_rate, samples, repetitions):
    x_array = np.linspace(min_error_rate, max_error_rate, samples)

    no_error = np.zeros(samples,dtype = np.uint16)

    error_detected = np.zeros(samples, dtype = np.uint16)
    error_not_detected = np.zeros(samples, dtype = np.uint16)

    error_corrected = np.zeros(samples, dtype = np.uint16)
    error_not_corrected= np.zeros(samples, dtype = np.uint16)
    
    def LogicalError(state):
        # return True if sum(state[:,0]) % 2 or sum(state[:,1])%2 else False
        return True if sum(state[:,0])%2 else False # only checks X errors

    for i in range(len(x_array)):
        now = dt.datetime.now()
        print(f'{now.strftime("%Y-%m-%d, %H:%M:%S")}: Physical error rate {x_array[i]}')
        for j in range(repetitions):
            bs13 = BaconShor13(x_array[i])
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

    return x_array, no_error, error_detected, error_not_detected, error_corrected, error_not_corrected



if __name__ == "__main__":
    # Generate Data
    repetitions = 100000
    x_tick_number = 100
    min_error_rate = 0
    max_error_rate = 1
    physical_error_rate, no_error, error_detected, error_not_detected, error_corrected, error_not_corrected = SimulateEncoding(min_error_rate, max_error_rate, x_tick_number, repetitions)

    data = np.vstack((physical_error_rate, no_error, error_detected, error_not_detected, error_corrected, error_not_corrected))

    data = np.transpose(data)
    np.savetxt(f"simulation_data_{repetitions}_{x_tick_number}_{min_error_rate}_{max_error_rate}_code_capacity.csv", data, delimiter = ",")


    # Load Data
    # data = np.loadtxt(f"simulation_data_{repetitions}_{x_tick_number}_{min_error_rate}_{max_error_rate}.csv", delimiter =",")

    # data = np.transpose(data)

    # physical_error_rate = data[0]
    # no_error = data[1].astype(np.uint16)
    # error_detected = data[2].astype(np.uint16)
    # error_not_detected = data[3].astype(np.uint16)
    # error_corrected = data[4].astype(np.uint16)
    # error_not_corrected = data[5].astype(np.uint16)


    # repetitions = 1000
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

    now = dt.datetime.now()
    fig, ax = plt.subplots()
    proportions = [failed_detection_rate+ total_error_not_corrected_rate]
    labels = [
        "Total Logical Error Rate"
        ]
    ax.stackplot(physical_error_rate*100, proportions,
                labels= labels)
    ax.plot(physical_error_rate*100,physical_error_rate*50)
    ax.legend(loc='upper left')
    ax.set_title('Logical Error Rate')
    ax.set_xlabel('Physical Error Rate')
    ax.set_ylabel('Logical Error Rate')
    # ax.set_xlim(min_error_rate,max_error_rate)
    # ax.set_ylim(0,100)

    fig.savefig("Logical Error Rate Plot Code Capacity.png")

    
    fig, ax = plt.subplots()
    proportions = [no_error_rate, total_error_corrected_rate, failed_detection_rate, total_error_not_corrected_rate]
    labels = [
        "No Error",
        "Error Corrected",
        "Undetected Logical Error",
        "Uncorrected Logical Error"
        ]
    ax.stackplot(physical_error_rate*100, proportions,
                labels= labels)
    ax.legend(loc='upper left')
    ax.set_title('Proportion')
    ax.set_xlabel('Physical Error Rate')
    ax.set_ylabel('Proportion')
    # ax.set_xlim(min_error_rate,max_error_rate)
    # ax.set_ylim(0,100)

    fig.savefig("Proportion of Results Code Capacity.png")
