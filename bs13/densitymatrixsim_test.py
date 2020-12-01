import cirq

def circuit(eps,kappa):

    qubits = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()
    circuit.append(cirq.X(qubits[0]))
    circuit.append(cirq.OverCNOT(eps,kappa).on(qubits[0],qubits[1]))
    circuit.append([cirq.measure(qubits[0], key ="q0"),cirq.measure(qubits[1],key="q1")])
    
    return circuit

if __name__== '__main__':
    eps=0   
    kappa =0 

    s = cirq.DensityMatrixSimulator()
    results = s.simulate(circuit(eps,kappa))

    print(results)
