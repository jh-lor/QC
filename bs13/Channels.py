import numpy as np
import math

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
        random = np.random.rand(1)[0]
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
        random = np.random.rand(1)[0]
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