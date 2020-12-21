import cirq
import numpy as np

def circuit(eps,kappa):

    qubits = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()

    #circuit.append(cirq.OverX(eps,kappa).on(qubits[0]))
    circuit.append(cirq.X(qubits[0]))
    circuit.append(cirq.X(qubits[1]))
    circuit.append(cirq.CNOT(qubits[0],qubits[1]))
    circuit.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[1]))
    circuit.append([cirq.measure(qubits[0], key ="q0"),cirq.measure(qubits[1], key ="q1")])
    
    return circuit

if __name__== '__main__':
    eps= 0
    kappa =0

    s = cirq.DensityMatrixSimulator()
    results = s.run(circuit(eps,kappa),repetitions = 10)
    print("eps: " + str(eps))
    print("kappa: "+ str(kappa))
    print(results.histogram(key='q0'))
    print(results.histogram(key='q1'))
