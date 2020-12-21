import cirq
import sys

pd = 0.0

sim = cirq.DensityMatrixSimulator()

def addCNOT(circ, qubits, uninvolved_qubits=[]):
    circ.append(cirq.I(q) for q in qubits + uninvolved_qubits)
    circ.append(cirq.CNOT(qubits[0], qubits[1]))
    circ.append(cirq.depolarize(pd)(qubits[0]))
    circ.append(cirq.depolarize(pd)(qubits[1]))


def prep(states, qubits):

    prep = cirq.Circuit()

    for i in range(len(states)):
        prep.append(cirq.I(q) for q in qubits[i])
        if states[i] == 1:
            prep.append(cirq.X(qubits[i][0]))
        addCNOT(prep, [qubits[i][0], qubits[i][2]])
        addCNOT(prep, [qubits[i][2], qubits[i][4]])

    preppedDM = sim.simulate(prep).final_density_matrix

    return preppedDM

def QEC(dm, qubits, uninvolved_qubits=[]):

    circ = cirq.Circuit()
    circ.append(cirq.I(q) for q in qubits + uninvolved_qubits)
    addCNOT(circ, [qubits[0], qubits[1]])
    addCNOT(circ, [qubits[2], qubits[1]])

    addCNOT(circ, [qubits[2], qubits[3]])
    addCNOT(circ, [qubits[4], qubits[3]])

    circ.append(cirq.measure(*(qubits[1], qubits[3]), key='synd'))
    circ.append(cirq.reset(qubits[1]))
    circ.append(cirq.reset(qubits[3]))

    res = sim.simulate(circ, initial_state=dm)
    s = res.measurements['synd'][0] + 2*res.measurements['synd'][1]

    if s == 2:
        corr = cirq.Circuit()
        corr.append(cirq.I(q) for q in qubits + uninvolved_qubits)
        corr.append(cirq.X(qubits[4]))
        ret = sim.simulate(corr, initial_state = res.final_density_matrix)
        return ret.final_density_matrix

    elif s == 3:
        corr = cirq.Circuit()
        corr.append(cirq.I(q) for q in qubits + uninvolved_qubits)
        corr.append(cirq.X(qubits[2]))
        ret = sim.simulate(corr, initial_state = res.final_density_matrix)
        return ret.final_density_matrix

    elif s == 1:
        corr = cirq.Circuit()
        corr.append(cirq.I(q) for q in qubits + uninvolved_qubits)
        corr.append(cirq.X(qubits[0]))
        ret = sim.simulate(corr, initial_state = res.final_density_matrix)
        return ret.final_density_matrix

    else:
        return res.final_density_matrix

def H(dm, qubits, uninvolved_qubits=[]):
    had = cirq.Circuit()

    had.append(cirq.I(q) for q in qubits + uninvolved_qubits)
    had.append(cirq.H(qubits[0]))
    addCNOT(had, [qubits[0], qubits[2]])
    addCNOT(had, [qubits[2], qubits[4]])

    return sim.simulate(had, initial_state = dm).final_density_matrix

def RZ(dm, theta, qubits, uninvolved_qubits=[]):
    z = cirq.Circuit()

    z.append(cirq.I(q) for q in qubits + uninvolved_qubits)
    z.append(cirq.rz(theta)(qubits[0]))

    return sim.simulate(z, initial_state = dm).final_density_matrix

def CNOTL(dm, qubits1, qubits2):
    logical_CNOT = cirq.Circuit()

    logical_CNOT.append(cirq.I(q) for q in qubits1 + qubits2)
    addCNOT(logical_CNOT, [qubits1[0], qubits2[0]])
    addCNOT(logical_CNOT, [qubits1[2], qubits2[2]])
    addCNOT(logical_CNOT, [qubits1[4], qubits2[4]])

    return sim.simulate(logical_CNOT, initial_state = dm).final_density_matrix

def CZpowL(dm, exp, qubits1, qubits2):
    logical_CZ = cirq.Circuit()

    logical_CZ.append(cirq.I(q) for q in qubits1 + qubits2)
    logical_CZ.append(cirq.CZPowGate(exponent = exp)(qubits1[0], qubits2[0]))

    return sim.simulate(logical_CZ, initial_state = dm).final_density_matrix

def meas(dm,qubits):
    m = cirq.Circuit()

    for i in range(len(qubits)):
        m.append(cirq.I(q) for q in qubits[i])
        m.append(cirq.measure(*(qubits[i][0], qubits[i][2], qubits[i][4]), key=str(i)))

    result = sim.simulate(m, initial_state = dm)
    out = []
    for i in range(len(qubits)):
        out.append(round(sum(result.measurements[str(i)])/3))
    return out


qb1 = cirq.LineQubit.range(5)
qb2 = cirq.LineQubit.range(5,10)


state = prep([0, 0], [qb1, qb2])
state = QEC(state, qb1, qb2)
state = QEC(state, qb2, qb1)

state = CNOTL(state, qb2, qb1)
state = RZ(state, 0.3, qb1, qb2)
state = CNOTL(state, qb2, qb1)
state = H(state, qb1, qb2)
state = H(state, qb2, qb1)

state = QEC(state, qb1, qb2)
state = QEC(state, qb2, qb1)

state = RZ(state, -0.5, qb1, qb2)
state = RZ(state, -0.5, qb1, qb2)
state = CNOTL(state, qb2, qb1)
state = RZ(state, 0.3, qb1, qb2)
state = CNOTL(state, qb2, qb1)
state = H(state, qb1, qb2)
state = H(state, qb2, qb1)
state = RZ(state, 0.5, qb1, qb2)
state = RZ(state, 0.5, qb1, qb2)

state = CZpowL(state, 0.75, qb1, qb2)

out = meas(state, [qb1, qb2])

print(out)
