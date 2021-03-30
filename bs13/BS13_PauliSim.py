import PauliSim

def BaconShor13():
    def __init__(self, p, state):
        self.errorRate = p
        self.measurements = {}

    def initialize(self):
        bs = PauliSim(13)
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

        sim.addZ(1)

        sim.addZStabilizer([0,3,1,4,2,5], 9)
        sim.addZStabilizer([3,6,4,7,5,8], 10)
        sim.addXStabilizer([0,1,3,4,6,7], 11)
        sim.addXStabilizer([1,2,4,5,7,8], 12)

        

        self.measurements['"Z1Z4Z2Z5Z3Z6"'] = 


if __name__ == "__main__":
