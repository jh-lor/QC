import cirq

qubits = cirq.LineQubit.range(2)

circuit = cirq.Circuit()

circuit.append(cirq.X(qubits[0]))
circuit.append(cirq.Z(qubits[1]))

s = cirq.DensityMatrixSimulator()

results = s.simulate(circuit)

# print("Circuit 1:")
# print(circuit)
# print(results)

print(results)
# print(results._final_simulator_state)
# print(results._final_simulator_state.density_matrix)
# print(results._final_simulator_state.density_matrix.reshape(4,4))
r = cirq.DensityMatrixSimulator()

circuit2 = cirq.Circuit()


circuit2.append(cirq.X(qubits[0]))
circuit2.append(cirq.X(qubits[0]))
circuit2.append(cirq.X(qubits[0]))
# circuit2.append(cirq.X(qubits[0]))
circuit2.append(cirq.Z(qubits[1]))
circuit2.append(cirq.Z(qubits[1]))
circuit2.append(cirq.Z(qubits[1]))



results2 =r.simulate(circuit2, initial_state = results._final_simulator_state.density_matrix.reshape(4,4))
# results2 =r.simulate(circuit2, initial_state = results._final_simulator_state)
# results2 =r.simulate(circuit2, initial_state= results)

print("Circuit 2:")
print(circuit2)
print(results2)