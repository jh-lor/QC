from PauliSim import PauliSim
import numpy as np

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
        for i in Xerr:
            sim.addX(i)
        
        for i in Zerr:
            sim.addZ(i)

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
        error_string += str(bs13.measurements["X1X2X4X5X7X8"])
        error_string += str(bs13.measurements["X2X3X5X6X8X9"])
        error_string += str(bs13.measurements["Z1Z4Z2Z5Z3Z6"])
        error_string += str(bs13.measurements["Z4Z7Z5Z8Z6Z9"]) 
        

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

    # def getState()

if __name__ == "__main__":
    # first test - don't add any noise to my gates 
    # call again regarding 
    # for x in range(9):
    #     for z in range(9):
    #         bs13 = BaconShor13()
    #         print("Xerr({}), Zerr({})".format(x,z))
    #         print(bs13.initialize([x]))
            # print(bs13.correctError())

    bs13 = BaconShor13(1)
    print(bs13.initialize())
    print(bs13.appliedchannels)


