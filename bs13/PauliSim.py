import numpy as np
from numba import njit
import math


class PauliSim():
    def __init__(self, size = None, initial_state = None):
        if type(initial_state) != type(None):
            self.state = initial_state.astype(bool)
        else:
            self.state = np.array(np.zeros(2*size).reshape(size,2), dtype = bool)
        self.operations = []

    def execute(self):
        for channel in self.operations:
            channel.apply(self.state)
        return self.state.astype(int)

    # def add(self, operation):
    #     self.operations.append(operation)

    def addDepolarizingNoise(self, qubits, p, number):
        channel = DepolarizingNoise(qubits,p, number)
        if number == 2:
            channel.addNoise2()
        elif number == 1:
            channel.addNoise1()
        self.operations.append(channel)

    def addX(self, target):
        channel = Gates(target)
        channel.X()
        self.operations.append(channel)
    
    def addZ(self, target):
        channel = Gates(target)
        channel.Z()
        self.operations.append(channel)

    def addH(self, target):
        channel = Gates(target)
        channel.H()
        self.operations.append(channel)

    def addY(self, target):
        channel = Gates(target)
        channel.Y()
        self.operations.append(channel)

    def addCNOT(self, target, control):
        channel = Gates(target, control)
        channel.CNOT()
        self.operations.append(channel)
    
    def addCZ(self, target, control):
        channel = Gates(target, control)
        channel.CZ()
        self.operations.append(channel)

    def addXStabilizer(self, qubits, stabilizer, p = 0):
        self.addH(stabilizer)
        for qubit in qubits:
            self.addCNOT(qubit, stabilizer)
            if p != 0:    
                self.addDepolarizingNoise([qubit, stabilizer], p, 2)
        self.addH(stabilizer)
    
    def addZStabilizer(self, qubits, stabilizer, p = 0):
        self.addH(stabilizer)
        for qubit in qubits:
            self.addCZ(qubit, stabilizer)
            if p != 0:
                self.addDepolarizingNoise([qubit, stabilizer], p, 2)
        self.addH(stabilizer)

    def getOperations(self):
        return [str(operation).lstrip() for operation in self.operations]


class BaseChannel():
    # implement super class for gates and noise
    def __init__(self, arr, target = None):
        self.gate = self.Ichannel
        self.str = ""
        self.arr = False
        self.target = target
        self.gate_list = []

    def apply(self,state):
        if self.arr:
            for gate in self.gate_list:
                gate.apply(state)
        else:
            self.gate(state)

    def __str__(self):
        return self.str

    def Xchannel(self, state):
        state[self.target][0] = not state[self.target][0]

    def Ychannel(self, state):
        state[self.target][0] = not state[self.target][0]
        state[self.target][1] = not state[self.target][1]

    def Zchannel(self, state):
        state[self.target][1] = not state[self.target][1]
    
    def Ichannel(self,state):
        return


class Gates(BaseChannel):
    def __init__(self, target, control = None):
        super().__init__(False, target)
        self.control = control 

    def I(self):
        self.gate = self.Ichannel
        self.str = "I({})".format(self.target)

    def X(self):
        self.gate = self.Xchannel
        self.str = "X({})".format(self.target)

    def Z(self):
        self.gate = self.Zchannel
        self.str = "Z({})".format(self.target)

    def H(self):
        def op(state):
            state[self.target][0], state[self.target][1] = state[self.target][1], state[self.target][0]
        self.gate = op
        self.str = "H({})".format(self.target)
        
    def Y(self):
        self.gate = self.Ychannel
        self.str = "Y({})".format(self.target)

    def CNOT(self):
        def op(state):
            state[self.control][0] = state[self.control][0]        
            state[self.target][0] =  (state[self.target][0] != state[self.control][0])
            state[self.control][1] = (state[self.target][1] != state[self.control][1])
            state[self.target][1] =  state[self.target][1]
        self.gate = op
        self.str = "CNOT({},{})".format(self.control, self.target)

    def CZ(self):
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
    def __init__(self, qubits, p, number): 
        self.arr = 1
        self.target = qubits
        self.str = ''
        self.number = number
        self.rate = p
        self.gate_list = []

    def addNoise1(self):
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
                    self.str += " Xerr("+str(i)+")"
                elif error_string[i] == "Y":
                    gate = Gates(qubit)
                    gate.Y()
                    self.gate_list.append(gate)
                    self.str += " Yerr("+str(i)+")"
                elif  error_string[i] == "Z":
                    gate = Gates(qubit)
                    gate.Z()
                    self.gate_list.append(gate)
                    self.str += " Zerr("+str(i)+")"
                else:
                    self.str +=" I({})".format(qubit)
            else: 
                self.str +=" I({})".format(qubit)

        # else:
        #     random = seed[0]
        #     if random< self.rate:
        #         if random < self.rate/3:
        #             gate = Gates(self.target)
        #             gate.X()
        #             self.gate = gate
        #             self.str += "Xerr("+str(self.target)+")"
        #         elif random < 2*self.rate/3:
        #             gate = Gates(self.target)
        #             gate.Y()
        #             self.gate = gate
        #             self.str += "Yerr("+str(self.target)+")"
        #         else:
        #             gate = Gates(self.target)
        #             gate.Z()
        #             self.gate = gate
        #             self.str += "Zerr("+str(self.target)+")"
        #     else: 
        #         gate = Gates(self.target)
        #         gate.I()
        #         self.gate = gate
        #         self.str +="I("+str(self.target)+")"

        

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
    
    

