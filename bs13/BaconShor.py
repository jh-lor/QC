from PauliSim import PauliSim
import numpy as np

class BaconShor13():
    """Implements a Bacon-Shor-13 simulation using the PauliSim class
    """
    def __init__(self, p = 0):
        """Initializes BaconShor object with error mode, physical error and initial state

        Args:
            mode (str): error mode for simuslation
            p (float, optional): physical error rate. Defaults to 0.
            state (numpy arr (int), optional): initial state of system. Defaults to None.
        """
        self.errorRate = p
        self.measurements = {}
        self.appliedchannels = []
        self.sim = PauliSim(13)

    def initialize_FT(self):
        """Intializes the Bacon-Shor-13 circuit with two qubit errors

        Args:
            Xerr (list, optional): list of index of qubits to append X gates to before stabilizers. For debugging purposes. Defaults to [].
            Zerr (list, optional): list of index of qubits to append Z gates to before stabilizers. For debugging purposes. Defaults to [].

        Returns:
            dict: dictionary of measurements. Keys are the stabilizer names.
        """
        self.sim.addTag("Fault Tolerant Initialization")
       
        self.sim.addCNOT(0,3) 
        self.sim.addCNOT(0,6)  

        for i in [0,3,6]:
            self.sim.addH(i)

        self.sim.addCNOT(0,1)
        self.sim.addDepolarizingNoise([0,1], self.errorRate, 2)

        self.sim.addCNOT(0,2)
        self.sim.addDepolarizingNoise([0,2], self.errorRate, 2)

        self.sim.addCNOT(3,4)
        self.sim.addDepolarizingNoise([3,4], self.errorRate, 2)

        self.sim.addCNOT(3,5)
        self.sim.addDepolarizingNoise([3,5], self.errorRate, 2)

        self.sim.addCNOT(6,7)
        self.sim.addDepolarizingNoise([6,7], self.errorRate, 2)

        self.sim.addCNOT(6,8)
        self.sim.addDepolarizingNoise([6,8], self.errorRate, 2)

        for i in range(0,9):
            self.sim.addH(i)      

    def single_qubit_errors(self):
        """Adds single qubit errors to each of nine data qubits
        """
        self.sim.addTag("Single Qubit Errors")
        for i in range(9):
            self.sim.addDepolarizingNoise(i, self.errorRate, 1)
    
    def add_errors(self, Xerr, Zerr):
        """[Debugging] Adds specific X or Z errors to the specified qubit

        Args:
            Xerr ([int]): list of qubits to apply X error to
            Zerr ([int]): list of qubits to apply Z error to
        """
        for qubit in Xerr:
            self.sim.addX(qubit)

        for qubit in Zerr:
            self.sim.addZ(qubit)

    def correctError(self):
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
 
        self.sim.addTag("Error Correction")

        for i in range(len(decode_string)):
            if decode_string[i] != 'I':
                if decode_string[i] =='X': 
                    self.sim.addX(i)
                if decode_string[i] =='Y': 
                    self.sim.addY(i)
                if decode_string[i] =='Z': 
                    self.sim.addZ(i)
    
    def measure_syndrome(self, error = False):
        """Appends stabilizers and measure the stabilizers. Resets ancilla qubits and clears the operations list after measurement

        Args:
            error (bool, optional): whether there is measurement error. Defaults to False.

        Returns:
            dict: dictionary of measurements. Keys are the stabilizer names.
        """
        
        self.sim.addTag("Stabilizer Measurement")

        if error:
            self.sim.addZStabilizer([0,3,1,4,2,5], 9, self.errorRate)
            self.sim.addZStabilizer([3,6,4,7,5,8], 10, self.errorRate)
            self.sim.addXStabilizer([0,1,3,4,6,7], 11, self.errorRate)
            self.sim.addXStabilizer([1,2,4,5,7,8], 12, self.errorRate)
        else:
            self.sim.addZStabilizer([0,3,1,4,2,5], 9)
            self.sim.addZStabilizer([3,6,4,7,5,8], 10)
            self.sim.addXStabilizer([0,1,3,4,6,7], 11)
            self.sim.addXStabilizer([1,2,4,5,7,8], 12)

        self.sim.addMeasurement(11, "X1X2X4X5X7X8")
        self.sim.addMeasurement(12, "X2X3X5X6X8X9")
        self.sim.addMeasurement(9, "Z1Z4Z2Z5Z3Z6")        
        self.sim.addMeasurement(10, "Z4Z7Z5Z8Z6Z9")

        # reset ancilla
        for i in [9, 10, 11 ,12]:
            self.sim.addReset(i)

        self.state = self.sim.execute()
        self.appliedchannels += self.sim.getOperations()
        self.measurements = self.sim.measurements

        #We reset the ancilla qubits and we need to reset the operations list as well for the next time we run the simulation
        self.sim.clear_operations()

        return self.measurements