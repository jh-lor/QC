# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 18:23:56 2020

@author: lorju


"""
import cirq
import sys
import datetime

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
'1110': 'IIIYIIIII',
'1111': 'IIIIYIIII',
'1101': 'IIIIIIIYI',
'0110': 'IIYIIIIII',
'0111': 'IIIIIYIII',
'0101': 'IIIIIIIIY'
}

size = 3**2+1
overrotation = False


def addX(circuit,qubits,theta,eps,kappa):
    circuit.append(cirq.rx(theta).on(qubits))
    if overrotation:
        circuit.append(cirq.OverX(eps,kappa).on(qubits))
    return

def addY(circuit,qubits,theta,eps,kappa):
    circuit.append(cirq.ry(theta).on(qubits))
    if overrotation:
        circuit.append(cirq.OverX(eps,kappa).on(qubits))
    return

def addZ(circuit,qubits,theta,eps,kappa):
    circuit.append(cirq.rz(theta).on(qubits))
    if overrotation:
        circuit.append(cirq.OverX(eps,kappa).on(qubits))
    return

def addH(circuit,qubits,eps,kappa):
    # error model not implemented yet
    circuit.append(cirq.H)
    if overrotation:
        pass
    return

def addCNOT(circuit, qubits,eps,kappa):
    circuit.append(cirq.CNOT(qubits[0],qubits[1]))
    if overrotation:
        circuit.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[1]))
    return

def addCZ(circuit,qubits,eps,kappa):
    circuit.append(cirq.CZ(qubits[0],qubits[1]))
    if overrotation:
        circuit.append(cirq.OverCZ(eps,kappa).on(qubits[0],qubits[1]))
    return

def addStabilizer(circuit,qubits, stab, XZ, qubits_list,eps,kappa):
    if XZ == "X":
        for i in qubits_list:
            circuit.append(cirq.H(qubits[i]))
            addCZ(circuit,[qubits[i],stab],eps,kappa)
            circuit.append(cirq.H(qubits[i]))
    if XZ == "Z":
        for i in qubits_list:
            addCZ(circuit,[qubits[i],stab],eps,kappa)

def fig2a(exponent, Zerr, Xerr,eps,kappa):
    """
    BS13 encoding. Applies X and Z gates after the encoding to simulate errors

    Parameters
    ----------
    exponent : float
        Exponent of Y gate
    Zerr : Int Arr
        Qubits that have a Z error
    Xerr : Int Arr
        Qubits that have a X error


    Returns
    -------
    fig2a : cirq.Circuit
        returns the appropriate circuit

    """
    #initialize 9 data qubits, 5 error qubits
    qubits = cirq.LineQubit.range(10)
    stab = qubits[9]
    
    
    fig2a = cirq.Circuit()
    
    #Non-fault tolerant enconding
    addY(fig2a, qubits[0],exponent,eps,kappa)
    addCNOT(fig2a,[qubits[0],qubits[3]],eps,kappa)
    addCNOT(fig2a,[qubits[0],qubits[6]],eps,kappa)

    fig2a.append(cirq.Moment([cirq.H(qubits[3]),cirq.H(qubits[6]),cirq.H(qubits[0])]))

    
    #fault tolerant encoding
    for pair in [(0,1),(0,2),(3,5),(6,7),(6,8),(3,4)]:
        x,y= pair
        addCNOT(fig2a,[qubits[x],qubits[y]],eps,kappa)
    
    fig2a.append(cirq.Moment(cirq.H(q) for q in qubits[:9]))
    
    # Test errors
    for z in Zerr:
        fig2a.append(cirq.Z(qubits[z]))
    for x in Xerr:
        fig2a.append(cirq.X(qubits[x]))
 

    #stabilizer initialization
    fig2a.append(cirq.H(stab))  

    #Z1Z4Z2Z5Z3Z6
    addStabilizer(fig2a,qubits,stab,"Z", [1,2,3,4,5,6],eps,kappa)
    fig2a.append(cirq.H(stab))
    fig2a.append(cirq.measure(stab,key="Z1Z4Z2Z5Z3Z6"))
    fig2a.append(cirq.reset(stab))
    
    #Z4Z7Z5Z8Z6Z9
    fig2a.append(cirq.H(stab))
    addStabilizer(fig2a,qubits, stab, "Z",[3,4,5,6,7,8],eps,kappa)
    fig2a.append(cirq.H(stab))
    fig2a.append(cirq.measure(stab,key="Z4Z7Z5Z8Z6Z9"))
    fig2a.append(cirq.reset(stab))
    
    #X1X2X4X5X7X8
    fig2a.append(cirq.H(stab))
    addStabilizer(fig2a,qubits,stab, "X", [0,1,3,4,6,7],eps,kappa)
    fig2a.append(cirq.H(stab))
    fig2a.append(cirq.measure(stab,key="X1X2X4X5X7X8"))
    fig2a.append(cirq.reset(stab))

    #X2X3X5X6X8X9
    fig2a.append(cirq.H(stab))
    addStabilizer(fig2a,qubits,stab, "X", [1,2,4,5,7,8],eps,kappa)
    fig2a.append(cirq.H(stab))
    fig2a.append(cirq.measure(stab,key="X2X3X5X6X8X9"))
    fig2a.append(cirq.reset(stab))

    return fig2a


def fig2a_Correct(circuit, error_string, eps, kappa):
    """
    Accepts a BS encoding and corrects a single error if it exists

    Parameters
    ----------
    circuit : cirq.Circuit
        BS13 encoding with measurement, possibly with an error that will be corrected
    lookup_table : Dict<String,String>
        Converts the bitstring from the stabilizer measurements into the appropriate error correction operations

    Returns
    -------
    circuit : cirq.Circuit
        returns original circuit with the appropriate operations appended and a new set of stabilizer measurements

    """
    circuit = cirq.Circuit()
    qubits = cirq.LineQubit.range(10)
    stab = qubits[9]
    # retrieve the required error correction
    decode_string = lookup_table.get(error_string)
 
    #initialize 9 data qubits, 5 error qubits
    print(decode_string)
    for i in range(len(decode_string)):
        if decode_string[i]!= 'I':
            # print(i, decode_string[i])
            if decode_string[i]=='X': circuit.append(cirq.X(qubits[i]))
            if decode_string[i]=='Y': circuit.append(cirq.Y(qubits[i]))
            if decode_string[i]=='Z': circuit.append(cirq.Z(qubits[i]))
    
    # append new measurements
    circuit.append(cirq.H(stab))
        
    #Z1Z4Z2Z5Z3Z6
    addStabilizer(circuit,qubits,stab, "Z", [1,2,3,4,5,6],eps,kappa)
    circuit.append(cirq.H(stab))
    circuit.append(cirq.measure(stab,key="Corrected Z1Z4Z2Z5Z3Z6"))
    circuit.append(cirq.reset(stab))
    
    #Z4Z7Z5Z8Z6Z9
    circuit.append(cirq.H(stab))
    addStabilizer(circuit,qubits, stab, "Z",[3,4,5,6,7,8],eps,kappa)
    circuit.append(cirq.H(stab))
    circuit.append(cirq.measure(stab,key="Corrected Z4Z7Z5Z8Z6Z9"))
    circuit.append(cirq.reset(stab))
    
    #X1X2X4X5X7X8
    circuit.append(cirq.H(stab))
    addStabilizer(circuit,qubits,stab, "X", [0,1,3,4,6,7],eps,kappa)
    circuit.append(cirq.H(stab))
    circuit.append(cirq.measure(stab,key="Corrected X1X2X4X5X7X8"))
    circuit.append(cirq.reset(stab))

    #X2X3X5X6X8X9
    circuit.append(cirq.H(stab))
    addStabilizer(circuit,qubits,stab, "X", [1,2,4,5,7,8],eps,kappa)
    circuit.append(cirq.H(stab))
    circuit.append(cirq.measure(stab,key="Corrected X2X3X5X6X8X9"))
    circuit.append(cirq.reset(stab))
    
    return circuit



if __name__=="__main__":

    # Xerr = [sys.argv[1]]
    # Zerr = [sys.argv[2]]
    # eps = sys.argv[3]
    # kappa = sys.argv[4]

    exponent = 0
    repetitions = 10
    Xerr= []
    Zerr = []
    eps = 0
    kappa = 1
    fig2a= fig2a(exponent, Zerr, Xerr,eps,kappa)

    # print(Zerr)
    # print(Xerr)  

    
    results_list = []

    for i in range(repetitions):
        # simulate encoding
        s= cirq.DensityMatrixSimulator()
        results = s.simulate(fig2a) 
        
        # create error string based on stabilizer measurement
        error_string = ''
        error_string+=str(results.measurements.get('X1X2X4X5X7X8')[0])
        error_string+=str(results.measurements.get('X2X3X5X6X8X9')[0]) 
        error_string+=str(results.measurements.get('Z1Z4Z2Z5Z3Z6')[0])
        error_string+=str(results.measurements.get('Z4Z7Z5Z8Z6Z9')[0])  

        results_dict = {} 
        for key in results.measurements.keys():
            results_dict[key] = results.measurements[key][0]   
        
        print("Error String: "+ error_string)


        final_state = results._final_simulator_state.density_matrix.reshape(2**size,2**size)

        # simulate error corrected circuit
        c= cirq.DensityMatrixSimulator()
        fig2a_Corrected = fig2a_Correct(fig2a, error_string,eps,kappa)
        

        corrected_results = c.simulate(fig2a_Corrected, initial_state = final_state)
        # print(corrected_results.measurements)

        corrected = True
        for key in corrected_results.measurements.keys():
            results_dict[key] = corrected_results.measurements[key][0]
            if corrected_results.measurements[key][0] == 1:
                corrected = False
        if corrected:
            print("Run "+ str(i+1) +": Corrected")
        else:
            print("Run "+ str(i+1) +": Stabilizers "+ str(results_dict))

        filename = "./bs13/test/"+str(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))+"_Run"+ str(i+1)+".txt"
        f = open(filename, "x")
        f.write(str(fig2a))
        f.write("\n\n")
        f.write(str(fig2a_Corrected))
        f.write("\n\n")
        f.write(str(results_dict))

        results_list.append((error_string, results_dict,corrected)) 