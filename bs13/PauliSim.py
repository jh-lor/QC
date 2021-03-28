import numpy as np

class PauliSim():
    def __init__(self, size):
        self.state = np.array(np.zeros(2*size).reshape(size,2), dtype = bool)
        self.operations = []

    def execute(self):
        for operation in self.operations:
            operation(self.state)
        return self.state.astype(int)

    def addX(self, target):
        self.operations.append(Gates(target).X)
    
    def addZ(self, target):
        self.operations.append(Gates(target).Z)

    def addH(self, target):
        self.operations.append(Gates(target).H)

    def addY(self, target):
        self.operations.append(Gates(target).Y)

    def addCNOT(self, target, control):
        self.operations.append(Gates(target, control).CNOT)
    
    def addCZ(self, target, control):
        self.operations.append(Gates(target, control).CZ)

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

    # def getOperations(self):
    #     return [str(operation) for operation in self.operations]


class Gates():
    def __init__(self, target, control = None):
        self.gate = None
        self.target = target
        self.control = control 

    def X(self, state):
        state[self.target][0] = not state[self.target][0]
        self.str = "X(",self.target,")"

    def Z(self, state):
        state[self.target][1] = not state[self.target][1]
        self.str = "Z(",self.target,")"

    def H(self, state):
        state[self.target][0], state[self.target][1] = state[self.target][1], state[self.target][0]
        self.str = "H(",self.target,")"
        
    def Y(self, state):
        state[self.target][0] = not state[self.target][0]
        state[self.target][1] = not state[self.target][1]
        self.str = "Y(",self.target,")"

    def CNOT(self, state):
        state[self.control][0] = state[self.control][0]        
        state[self.target][0] =  (state[self.target][0] != state[self.control][0])
        state[self.control][1] = (state[self.target][1] != state[self.control][1])
        state[self.target][1] =  state[self.target][1]
        self.str = "CNOT(",self.control,",",self.target,")"

    def CZ(self, state):
        self.H(state)
        self.CNOT(state)
        self.H(state)
        self.str = "CZ(",self.control,",",self.target,")"

    # def __str__(self):
    #     return self.str


if __name__ == "__main__":
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
    sim.addZ(1)

    sim.addZStabilizer([0,3,1,4,2,5], 9)
    sim.addZStabilizer([3,6,4,7,5,8], 10)
    sim.addXStabilizer([0,1,3,4,6,7], 11)
    sim.addXStabilizer([1,2,4,5,7,8], 12)

    print(sim.execute())
    
    

