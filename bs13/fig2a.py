# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 18:23:56 2020

@author: lorju


"""
import cirq


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
    qubits = cirq.LineQubit.range(14)
    stab = qubits[9:]
    
    
    fig2a = cirq.Circuit()
    
    #Non-fault tolerant enconding
    fig2a.append(cirq.YPowGate(exponent = exponent).on(qubits[0]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[3]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[6]))

    fig2a.append(cirq.Moment([cirq.H(qubits[3]),cirq.H(qubits[6]),cirq.H(qubits[0])]))

    
    #fault tolerant encoding
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[1]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[2]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[3],qubits[5]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[6],qubits[7]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[6],qubits[8]))
    fig2a.append(cirq.OverCNOT(eps,kappa).on(qubits[3],qubits[4]))
    
    fig2a.append(cirq.Moment(cirq.H(q) for q in qubits[:9]))
    
    # Test errors
    for z in Zerr:
        fig2a.append(cirq.Z(qubits[z]))
    for x in Xerr:
        fig2a.append(cirq.X(qubits[x]))
 
    for i in range(4):
        fig2a.append(cirq.H(stab[i]))
        

    #Z1Z4Z2Z5Z3Z6
    for i in range(6):
        fig2a.append(cirq.OverCZ(eps,kappa).on(qubits[i],stab[0]))

    
    #Z4Z7Z5Z8Z6Z9
    for i in [3,4,5,6,7,8]:
        fig2a.append(cirq.OverCZ(eps,kappa).on(qubits[i],stab[1]))

    #X1X2X4X5X7X8
    for i in [0,1,3,4,6,7]:
        fig2a.append(cirq.H(qubits[i]))
        fig2a.append(cirq.OverCZ(eps,kappa).on(qubits[i],stab[2]))
        fig2a.append(cirq.H(qubits[i]))
        
    #X2X3X5X6X8X9
    for i in [1,2,4,5,7,8]:
        fig2a.append(cirq.H(qubits[i]))
        fig2a.append(cirq.OverCZ(eps,kappa).on(qubits[i],stab[3]))
        fig2a.append(cirq.H(qubits[i]))
    
    
    fig2a.append(cirq.Moment(cirq.H(stab[i]) for i in range(4)))
        
    fig2a.append(cirq.Moment([cirq.measure(stab[3],key="X2X3X5X6X8X9"),cirq.measure(stab[2],key="X1X2X4X5X7X8"),cirq.measure(stab[1],key="Z4Z7Z5Z8Z6Z9"),cirq.measure(stab[0],key="Z1Z4Z2Z5Z3Z6")]))
    
    return fig2a


def fig2a_Correct(circuit,lookup_table):
    """
    Accepts a BS encoding and corrects a single error if it exists

    Parameters
    ----------
    circuit : cirq.Circuit
        BS13 encoding with measurement, possibily with an error that will be corrected
    lookup_table : Dict<String,String>
        Converts the bitstring from the stabilizer measurements into the appropriate error correction operations

    Returns
    -------
    circuit : cirq.Circuit
        returns original circuit with the appropriate operations appended and a new set of stabilizer measurements

    """
    s= cirq.Simulator()
    results = s.simulate(circuit)
    error_string = ''
    
    # create error string based on stabilizer measurement
    error_string+=str(results.measurements.get('X1X2X4X5X7X8')[0])
    error_string+=str(results.measurements.get('X2X3X5X6X8X9')[0]) 
    error_string+=str(results.measurements.get('Z1Z4Z2Z5Z3Z6')[0])
    error_string+=str(results.measurements.get('Z4Z7Z5Z8Z6Z9')[0])
    
    
    print(error_string)
    # retrieve the required error correction
    decode_string = lookup_table.get(error_string)
 
    #initialize 9 data qubits, 5 error qubi(ts
    qubits = cirq.LineQubit.range(18)
    stab = qubits[9:14]
    stab_corrected = qubits[14:]
    print(decode_string)
    for i in range(len(decode_string)):
        if decode_string[i]!= 'I':
            if decode_string[i]=='X': circuit.append(cirq.Moment(cirq.X(qubits[i])))
            if decode_string[i]=='Y': circuit.append(cirq.Moment(cirq.Y(qubits[i])))
            if decode_string[i]=='Z': circuit.append(cirq.Moment(cirq.Z(qubits[i])))
    
    # append new measurements
    for i in range(4):
        circuit.append(cirq.H(stab_corrected[i]))
        
    #Z1Z4Z2Z5Z3Z6
    for i in range(6):
        circuit.append(cirq.CZ(qubits[i],stab_corrected[0]))

    
    #Z4Z7Z5Z8Z6Z9
    for i in [3,4,5,6,7,8]:
        circuit.append(cirq.CZ(qubits[i],stab_corrected[1]))

    #X1X2X4X5X7X8
    for i in [0,1,3,4,6,7]:
        circuit.append(cirq.H(qubits[i]))
        circuit.append(cirq.CZ(qubits[i],stab_corrected[2]))
        circuit.append(cirq.H(qubits[i]))
        
    #X2X3X5X6X8X9

    for i in [1,2,4,5,7,8]:
        circuit.append(cirq.H(qubits[i]))
        circuit.append(cirq.CZ(qubits[i],stab_corrected[3]))
        circuit.append(cirq.H(qubits[i]))
    
    
    circuit.append(cirq.Moment(cirq.H(stab_corrected[i]) for i in range(4)))
        
    circuit.append(cirq.Moment(cirq.measure(stab_corrected[3],key="Corrected X2X3X5X6X8X9"),cirq.measure(stab_corrected[2],key="Corrected X1X2X4X5X7X8"),cirq.measure(stab_corrected[1],key="Corrected Z4Z7Z5Z8Z6Z9"),cirq.measure(stab_corrected[0],key="Corrected Z1Z4Z2Z5Z3Z6")))
    
    return circuit



if __name__=="__main__":
    exponent = 0
    repetitions = 5
    Zerr = [0]
    Xerr= []
    eps = 0
    kappa = 0
    fig2a= fig2a(exponent, Zerr, Xerr,eps,kappa)
    
    s= cirq.Simulator()
    results = s.simulate(fig2a)
    for i in range(repetitions):
        each_rep = {}
        for key in results.measurements.keys():
            each_rep[key] = results.measurements[key][0]
    
        print("Run "+ str(i+1) +": Stabilizers "+ str(each_rep))
    
    
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
    
    
    fig2a_Corrected = fig2a_Correct(fig2a, lookup_table)
    
    s= cirq.Simulator()
    results = s.simulate(fig2a_Corrected)
    # density matrix simulator
    # make gates have errors in the them
    # measurement outcome to have some probability distribution
    # pip install -e to the directory, add in a few extra gates 
    #   Ion trap compiled
    for i in range(repetitions):
        each_rep = {}
        corrected = True
        for key in results.measurements.keys():
            if "Corrected" in key:
                each_rep[key] = results.measurements[key][0]
                if results.measurements[key][0] == 1:
                    corrected = False
        if corrected:
            print("Run "+ str(i+1) +": Corrected")
        else:
            print("Run "+ str(i+1) +": Stabilizers "+ str(each_rep))
    
    