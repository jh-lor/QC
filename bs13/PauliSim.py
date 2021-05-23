import numpy as np
from numba import njit
import math


class PauliSim():
    """PauliSim class is a PauliSimulator. The error on each qubit is maintained as a size-2 array
    for X and Z errors and a list of operations to apply on the qubits is maintained
    """
    def __init__(self, size = None, initial_state = None):
        """ PauliSim class is a PauliSimulator. The error on each qubit is maintained as a size-2 array
        for X and Z errors and a list of operations to apply on the qubits is maintained

        Args:
            size (int, optional): Number of qubits to simulate. Defaults to None.
            initial_state (numpy arr (int), optional): Initial State of PauliSim. Defaults to None.
        """
        if type(initial_state) != type(None):
            self.state = initial_state.astype(bool)
        else:
            self.state = np.array(np.zeros(2*size).reshape(size,2), dtype = bool)
        self.operations = []
        self.measurements = {}

    def execute(self):
        """Applies all the operations in the operation list to the error state

        Returns:
            numpy array (int): error state of system 
        """
        for channel in self.operations:
            channel.apply(self.state)
        return self.state.astype(int)

    # def add(self, operation):
    #     self.operations.append(operation)

    def addTag(self, tag):
        tagger = BaseChannel(False)
        tagger.tag(tag)
        self.operations.append(tagger)

    def addReset(self, target):
        channel = Gates(target)
        channel.Reset()
        self.operations.append(channel)
    
    def addMeasurement(self, target, key):
        channel = Gates(target)
        channel.Measure(key, self.measurements)
        self.operations.append(channel)

    def addDepolarizingNoise(self, qubits, p, number):
        """Adds depolarizing noise channel to one or two qubits

        Args:
            qubits (arr): qubits to apply depolarizing noise to
            p (float): physical error rate of depolarizing channel
            number (int): number of qubits to apply noise to
        """
        channel = DepolarizingNoise(qubits,p, number)
        if number == 2:
            channel.addNoise2()
        elif number == 1:
            channel.addNoise1()
        self.operations.append(channel)

    def addX(self, target):
        """Append X gate on a target qubit to operations list

        Args:
            target (int): qubit index
        """
        channel = Gates(target)
        channel.X()
        self.operations.append(channel)
    
    def addZ(self, target):
        """Append Z gate on a target qubit to operations list

        Args:
            target (int): qubit index
        """
        channel = Gates(target)
        channel.Z()
        self.operations.append(channel)

    def addH(self, target):
        """Append H gate on a target qubit to operations list

        Args:
            target (int): qubit index
        """
        channel = Gates(target)
        channel.H()
        self.operations.append(channel)

    def addY(self, target):
        """Append Y gate on a target qubit to operations list

        Args:
            target (int): qubit index
        """
        channel = Gates(target)
        channel.Y()
        self.operations.append(channel)

    def addCNOT(self, target, control):
        """Append a CNOT gate on a target qubit and control qubit to operations list

        Args:
            target (int): target qubit index
            control (int): control qubit index
        """
        channel = Gates(target, control)
        channel.CNOT()
        self.operations.append(channel)
    
    def addCZ(self, target, control):
        """Append a CZ gate on a target qubit and control qubit to operations list

        Args:
            target (int): target qubit index
            control (int): control qubit index
        """
        channel = Gates(target, control)
        channel.CZ()
        self.operations.append(channel)

    def addXStabilizer(self, qubits, ancilla, p = 0):
        """Append CNOT gates on the qubits and the specificied ancilla to form a X stabilizer

        Args:
            qubits (numpy arr (int)): list of qubits in the X stabilizer 
            ancilla (int): ancilla qubit carrying the stabilizer state
            p (int, optional): physical error rate of the CNOT gates. Defaults to 0.
        """
        self.addH(ancilla)
        for qubit in qubits:
            self.addCNOT(qubit, ancilla)
            if p > 0:    
                self.addDepolarizingNoise([qubit, ancilla], p, 2)
        self.addH(ancilla)
    
    def addZStabilizer(self, qubits, ancilla, p = 0):
        """Append CZ gates on the qubits and the specificied ancilla to form a Z stabilizer

        Args:
            qubits (numpy arr (int)): list of qubits in the Z stabilizer 
            ancilla (int): ancilla qubit carrying the stabilizer state
            p (int, optional): physical error rate of the CNOT gates. Defaults to 0.
        """
        self.addH(ancilla)
        for qubit in qubits:
            self.addCZ(qubit, ancilla)
            if p > 0:
                self.addDepolarizingNoise([qubit, ancilla], p, 2)
        self.addH(ancilla)

    def getOperations(self):
        """Returns list of operations in readable format

        Returns:
            list (str): string representation of the operation list
        """
        return [str(operation).lstrip() for operation in self.operations]


class BaseChannel():
    """Pauli Channels are implemented here
    """
    def __init__(self, arr, target = None):
        """Initializes variables defining function of channels. gate_list and arr are implemented in case the channel comprises more than one qubit

        Args:
            arr (bool): if channel gates is in an array i.e. channel comprises more than one qubit
            target (int , optional): target qubit of the channel. Defaults to None.
        """
        self.gate = self.Ichannel
        self.str = ""
        self.arr = False
        self.target = target
        self.gate_list = []

    def apply(self,state):
        """Applies the gate in the gate variable or gates in gate_list if there are more than one gate in the channel

        Args:
            state (numpy arr (bool)): error matrix of PauliSim
        """
        if self.arr:
            for gate in self.gate_list:
                gate.apply(state)
        else:
            self.gate(state)

    def __str__(self):
        return self.str

    def tag(self, string):
        self.str = string

    def reset_channel(self,state):
        """Resets both X and Z bits to 0

        Args:
            state (numpy arr (bool)): error matrix of PauliSim
        """
        state[self.target][0] = False
        state[self.target][1] = False


    def Xchannel(self, state):
        """Pauli X channel

        Args:
            state (numpy arr (bool)): error matrix of PauliSim
        """
        state[self.target][0] = not state[self.target][0]

    def Ychannel(self, state):
        """Pauli Y channel

        Args:
            state (numpy arr (bool)): error matrix of PauliSim
        """
        state[self.target][0] = not state[self.target][0]
        state[self.target][1] = not state[self.target][1]

    def Zchannel(self, state):
        """Pauli Z channel

        Args:
            state (numpy arr (bool)): error matrix of PauliSim
        """
        state[self.target][1] = not state[self.target][1]
    
    def Ichannel(self,state):
        return


class Gates(BaseChannel):
    """Implements common gates

    Args:
        BaseChannel (class): inherits apply and channel methods
    """
    def __init__(self, target, control = None):
        """Initializes BaseChannel variables and control variable if gate is a control gate

        Args:
            target (int): target qubit index
            control (int, optional): control qubit index. Defaults to None.
        """
        super().__init__(False, target)
        self.control = control 

    def Reset(self):
        """Sets gate to Reset and updates the gate string
        """
        self.gate = self.reset_channel
        self.str = f"Reset({self.target})"

    def Measure(self, key, dict):

        def measure(state):
            dict[key] = state[self.target][0].astype(int)
        self.gate = measure
        self.str = f"M({key})"


    def I(self):
        """Sets gate to Identity gate and updates the gate string
        """
        self.gate = self.Ichannel
        self.str = "I({})".format(self.target)

    def X(self):
        """Sets gate to X gate and updates the gate string
        """
        self.gate = self.Xchannel
        self.str = "X({})".format(self.target)

    def Z(self):
        """Sets gate to Z gate and updates the gate string
        """
        self.gate = self.Zchannel
        self.str = "Z({})".format(self.target)

    def H(self):
        """Sets gate to H gate and updates the gate string
        """
        def op(state):
            state[self.target][0], state[self.target][1] = state[self.target][1], state[self.target][0]
        self.gate = op
        self.str = "H({})".format(self.target)
        
    def Y(self):
        """Sets gate to Y gate and updates the gate string
        """
        self.gate = self.Ychannel
        self.str = "Y({})".format(self.target)

    def CNOT(self):
        """Sets gate to CNOT gate and updates the gate string
        """
        def op(state):
            state[self.control][0] = state[self.control][0]        
            state[self.target][0] =  (state[self.target][0] != state[self.control][0])
            state[self.control][1] = (state[self.target][1] != state[self.control][1])
            state[self.target][1] =  state[self.target][1]
        self.gate = op
        self.str = "CNOT({},{})".format(self.control, self.target)

    def CZ(self):
        """Sets gate to CZ gate and updates the gate string
        """
        def op(state):
            # H
            state[self.target][0], state[self.target][1] = state[self.target][1], state[self.target][0]

            # CNOT
            state[self.control][0] = state[self.control][0]        
            state[self.target][0] =  (state[self.target][0] != state[self.control][0])
            state[self.control][1] = (state[self.target][1] != state[self.control][1])
            state[self.target][1] =  state[self.target][1]

            # H
            state[self.target][0], state[self.target][1] = state[self.target][1], state[self.target][0]

        self.gate = op
        self.str = "CZ({},{})".format(self.control, self.target)

class DepolarizingNoise(BaseChannel):
    """Implements depolarizing noise on one and two qubits

    Args:
        BaseChannel (class): inherits the apply and channel methods
    """
    def __init__(self, qubits, p, number): 
        """Initializes variables for error channel

        Args:
            qubits (int/list (int)): qubit or list of qubits the noise channel acts on
            p (float): physical error rate
            number (int): number of qubits the channel acts on
        """
        self.arr = 1
        self.target = qubits
        self.str = ''
        self.number = number
        self.rate = p
        self.gate_list = []

    def addNoise1(self):
        """Randomly appends a Pauli channel to the target qubit depending on the physical error rate
        """
        error_table = {
            1 : "X",
            2 : "Y",
            3 : "Z"
        }
        random = np.random.rand(1) 
        qubit = self.target
        if random < self.rate:
            error_string = error_table[math.ceil(random/self.rate*3)]
            gate = Gates(qubit)
            if error_string == "X":
                gate.X()
                self.gate_list.append(gate)
                self.str += f" Xerr({qubit})"
            elif error_string == "Y":
                gate.Y()
                self.gate_list.append(gate)
                self.str += f" Yerr({qubit})"
            elif  error_string == "Z":
                gate.Z()
                self.gate_list.append(gate)
                self.str += f" Zerr({qubit})"
            else:
                gate.I()
                self.gate_list.append(gate)
                self.str += " I({})".format(qubit)
        else: 
            gate = Gates(qubit)
            gate.I()
            self.gate_list.append(gate)
            self.str +=" I({})".format(qubit)

    def addNoise2(self):
        """Randomly appends Pauli channels to target qubits depending on the physical error rate
        """
        error_table = {
            1 : "IX",
            2 : "IY",
            3 : "IZ",
            4 : "XI",
            5 : "XX",
            6 : "XY",
            7 : "XZ",
            8 : "YI",
            9 : "YX",
            10 : "YY",
            11 : "YZ",
            12 : "ZI",
            13 : "ZX",
            14 : "ZY",
            15 : "ZZ"
        }
        seed = np.random.rand(1) 
        random = seed[0]
        for i in range(self.number):
            qubit = self.target[i]
            if random < self.rate:
                error_string = error_table[math.ceil(random/self.rate *15)]                
                if error_string[i] == "X":
                    gate = Gates(qubit)
                    gate.X()
                    self.gate_list.append(gate)
                    self.str += " Xerr("+str(qubit)+")"
                elif error_string[i] == "Y":
                    gate = Gates(qubit)
                    gate.Y()
                    self.gate_list.append(gate)
                    self.str += " Yerr("+str(qubit)+")"
                elif  error_string[i] == "Z":
                    gate = Gates(qubit)
                    gate.Z()
                    self.gate_list.append(gate)
                    self.str += " Zerr("+str(qubit)+")"
                else:
                    self.str +=" I({})".format(qubit)
            else: 
                self.str +=" I({})".format(qubit)
       

if __name__ == "__main__":
    # Debugging
    errorRate = 0.1
    for i in range(100):
        sim = PauliSim(13)

        sim.addCNOT(0,3) 
        sim.addCNOT(0,6)  

        for i in [0,3,6]:
            sim.addH(i)

        sim.addCNOT(0,1)
        sim.addDepolarizingNoise([0,1], errorRate, 2)
        sim.addCNOT(0,2)
        sim.addDepolarizingNoise([0,2], errorRate, 2)

        sim.addCNOT(3,4)
        sim.addDepolarizingNoise([3,4], errorRate, 2)
        sim.addCNOT(3,5)
        sim.addDepolarizingNoise([3,5], errorRate, 2)

        sim.addCNOT(6,7)
        sim.addDepolarizingNoise([6,7], errorRate, 2)
        sim.addCNOT(6,8)
        sim.addDepolarizingNoise([6,8], errorRate, 2)

        for i in range(0,9):
            sim.addH(i)

        # Add Errors Here
        # sim.addZ(0)
        # sim.addX(0)

        sim.addZStabilizer([0,3,1,4,2,5], 9)
        sim.addZStabilizer([3,6,4,7,5,8], 10)
        sim.addXStabilizer([0,1,3,4,6,7], 11)
        sim.addXStabilizer([1,2,4,5,7,8], 12)
        print(sim.execute())
    

    # for i in range(100):
    #     sim = PauliSim(2)
    #     target = 0
    #     sim.addDepolarizingNoise(target,0.1,1)
    #     print(sim.execute())
        
    # print("\n")
    
    

