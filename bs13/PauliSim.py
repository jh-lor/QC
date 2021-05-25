import numpy as np
from Channels import *


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

    def clear_operations(self):
        self.operations = []

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
    
    

