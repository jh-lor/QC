import numpy as np

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

    def addDepolarizingNoise(self, qubits, p):
        channel = DepolarizingNoise(qubits,p)
        channel.addNoise()
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

    def addXStabilizer(self, qubits, stabilizer):
        self.addH(stabilizer)
        for qubit in qubits:
            self.addCNOT(qubit, stabilizer)
        self.addH(stabilizer)
    
    def addZStabilizer(self, qubits, stabilizer):
        self.addH(stabilizer)
        for qubit in qubits:
            self.addCZ(qubit, stabilizer)
        self.addH(stabilizer)

    def getOperations(self):
        return [str(operation) for operation in self.operations]

class BaseChannel():
    # implement super class for gates and noise
    def __init__(self, arr):
        self.gate = None
        self.str = ""
        self.arr = False

    def apply(self,state):
        if self.arr:
            for channel in self.gate:
                channel(state)
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

class Gates(BaseChannel):
    def __init__(self, target, control = None, p = 0):
        super().__init__(False)
        self.target = target
        self.control = control 
        self.rate = p
        
    def I(self):
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
    def __init__(self, qubits, p):
        super().__init__(True)
        self.qubits = qubits
        self.number = len(qubits)
        self.rate = p
        self.gate = []
        self.arr = True

    def addNoise(self):
        # only implemented noise for 1 and 2 qubits
        seed = np.random.rand(self.number)
        
        for i in range(len(self.qubits)):
            random = seed[i]
            qubit = self.qubits[i]
            if random < self.rate:
                if self.number == 1:
                    if random < self.rate/3:
                        self.gates.append(self.Xchannel)
                        self.str += "Xerr(",i,")"
                    elif random < 2*self.rate/3:
                        self.gates.append(self.Ychannel)
                        self.str += "Yerr(",i,")"
                    else:
                        self.gates.append(self.Zchannel)
                        self.str += "Zerr(",i,")"

                if self.number == 2:
                    if random < 4*self.rate/15:
                        sself.gates.append(self.Xchannel)
                        self.str += "Xerr(",i,")"
                    elif random < 8*self.rate/15:
                        self.gates.append(self.Ychannel)
                        self.str += "Yerr(",i,")"
                    elif random < 12*self.rate/15:
                        self.gates.append(self.Zchannel)
                        self.str += "Zerr(",i,")"
                    else:
                        self.str ="I({})".format(qubit)
                else: 
                    self.str ="I({})".format(qubit)

if __name__ == "__main__":
    # Debugging
    sim = PauliSim(13)

    sim.addCNOT(0,3) 
    sim.addCNOT(0,6)  

    for i in [0,3,6]:
        sim.addH(i)

    sim.addCNOT(0,1)
    sim.addCNOT(0,2)

    sim.addCNOT(3,4)
    sim.addCNOT(3,5)

    sim.addCNOT(6,7)
    sim.addCNOT(6,8)

    for i in range(0,9):
        sim.addH(i)

    # Add Errors Here
    sim.addZ(0)
    sim.addX(0)

    sim.addZStabilizer([0,3,1,4,2,5], 9)
    sim.addZStabilizer([3,6,4,7,5,8], 10)
    sim.addXStabilizer([0,1,3,4,6,7], 11)
    sim.addXStabilizer([1,2,4,5,7,8], 12)
    print(sim.execute())
    
    # sim = PauliSim(1)
    # sim.addX(0)
    # print(sim.getOperations())
    # print(sim.execute())
    # for i in range(100):
    #     sim = PauliSim(2)
    #     sim.addDepolarizingNoise([0,1],0.5)
    #     print(sim.execute())
    #     print("\n")
    
    

