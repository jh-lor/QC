import numpy as np
from quantumsim.sparsedm import SparseDM
import json
import time
import sys
import quantumsim.circuit
from numpy import prod
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import itertools

epsilon = 0.1 #IARPA TEM
eps = epsilon
epsilon1q = 0.02 #0.02 if no crosstalk
kap = 0
RabiRatio = 0.0
RabiRatio1Q = 0.0
pm = 0.005
pp = 0.001
d2q = 0.0
d1q = 0

epsilon = 0.05
eps = epsilon
epsilon1q = 0.01
kap = 1
RabiRatio = 0.0
RabiRatio1Q = 0.0
pm = 0.0
pp = 0.00
d2q = 0.05
d1q = 0.05

epsilon = 0.067 #LQ paper
# epsilon = 0.067
eps = epsilon
epsilon1q = 0.01
kap = 0
RabiRatio = 0.0
RabiRatio1Q = 0.0
pm = 0.005
pp = 0.001
d2q = 0.0
d1q = 0.0

epsperms = 0.00



chain = [ 'd0', 'd1', 'd2', 's0', 'd3', 'd4', 'd5', 's1', 'd6', 'd7', 'd8']

def addCrosstalk(circ, qubits, t):

    if chain.index(qubits[0]) < chain.index(qubits[1]):
        left = qubits[0]
        right = qubits[1]
    else:
        left = qubits[1]
        right = qubits[0]

    if abs(chain.index(qubits[0]) - chain.index(qubits[1])) == 1:

        if chain.index(left) != 0:
            circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(left) - 1], time = t + 0.01, chi = RabiRatio*np.pi/4))
            circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(left) - 1], time = t + 0.02, chi = RabiRatio*np.pi/4))

        if chain.index(right) != len(chain)-1:
            circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(right) + 1], time = t + 0.03, chi = RabiRatio*np.pi/4))
            circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(right) + 1], time = t + 0.04, chi = RabiRatio*np.pi/4))

    elif abs(chain.index(qubits[0]) - chain.index(qubits[1])) == 2:

        if chain.index(left) != 0:
            circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(left) - 1], time = t + 0.01, chi = RabiRatio*np.pi/4))
            circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(left) - 1], time = t + 0.02, chi = RabiRatio*np.pi/4))

        if chain.index(right) != len(chain)-1:
            circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(right) + 1], time = t + 0.03, chi = RabiRatio*np.pi/4))
            circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(right) + 1], time = t + 0.04, chi = RabiRatio*np.pi/4))

        circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(right) - 1], time = t + 0.05, chi = 2*RabiRatio*np.pi/4))
        circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(right) - 1], time = t + 0.06, chi = 2*RabiRatio*np.pi/4))


    else:

        if chain.index(left) != 0:
            circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(left) - 1], time = t + 0.01, chi = RabiRatio*np.pi/4))
            circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(left) - 1], time = t + 0.02, chi = RabiRatio*np.pi/4))

        if chain.index(right) != len(chain)-1:
            circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(right) + 1], time = t + 0.03, chi = RabiRatio*np.pi/4))
            circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(right) + 1], time = t + 0.04, chi = RabiRatio*np.pi/4))

        circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(right) - 1], time = t + 0.05, chi = RabiRatio*np.pi/4))
        circ.add_gate(quantumsim.circuit.XX(right, chain[chain.index(left) + 1], time = t + 0.06, chi = RabiRatio*np.pi/4))
        circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(right) - 1], time = t + 0.07, chi = RabiRatio*np.pi/4))
        circ.add_gate(quantumsim.circuit.XX(left, chain[chain.index(left) + 1], time = t + 0.08, chi = RabiRatio*np.pi/4))

def addXX(circ, qubits, t):
    global epsilon
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[0],time = t - 0.01, angle = d2q*np.pi/8))
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[1],time = t - 0.01, angle = d2q*np.pi/8))
    circ.add_gate(quantumsim.circuit.XX(qubits[0],qubits[1], time = t, chi = np.pi/4))
    circ.add_gate(quantumsim.circuit.OverXX(qubits[0],qubits[1], time = t + 0.0001, theta = (epsilon*epsilon + 2*epsilon)*np.pi/4, kappa = kap))
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[0],time = t + 0.001, angle = d2q*np.pi/8))
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[1],time = t + 0.001, angle = d2q*np.pi/8))
    # addCrosstalk(circ, qubits, t)
    epsilon+=epsperms

def addXXm(circ, qubits, t):
    global epsilon
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[0],time = t - 0.01, angle = d2q*np.pi/8))
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[1],time = t - 0.01, angle = d2q*np.pi/8))
    circ.add_gate(quantumsim.circuit.XX(qubits[0],qubits[1], time = t, chi = -np.pi/4))
    circ.add_gate(quantumsim.circuit.OverXX(qubits[0],qubits[1], time = t + 0.0001, theta = -1*(epsilon*epsilon + 2*epsilon)*np.pi/4, kappa = kap))
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[0],time = t + 0.001, angle = d2q*np.pi/8))
    circ.add_gate(quantumsim.circuit.RotateZ(qubits[1],time = t + 0.001, angle = d2q*np.pi/8))
    # addCrosstalk(circ, qubits, t)
    epsilon+=epsperms



def addRX(circ, qubit, ang, t):
    circ.add_gate(quantumsim.circuit.RotateZ(qubit, time = t - 0.01, angle = d1q*ang/2))

    circ.add_gate(quantumsim.circuit.RotateX(qubit, time = t, angle = ang))
    circ.add_gate(quantumsim.circuit.OverX(qubit, time = t + 0.0001, theta = epsilon1q*ang, kappa = kap))

    # if chain.index(qubit) == 0:
    #     circ.add_gate(quantumsim.circuit.RotateX(chain[1], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #
    # elif chain.index(qubit) == len(chain) - 1:
    #     circ.add_gate(quantumsim.circuit.RotateX(chain[-2], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #
    # else:
    #     circ.add_gate(quantumsim.circuit.RotateX(chain[chain.index(qubit) - 1], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #     circ.add_gate(quantumsim.circuit.RotateX(chain[chain.index(qubit) + 1], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #
    #     circ.add_gate(quantumsim.circuit.RotateZ(qubit, time = t + 0.01, angle = d1q*ang/2))

def addRY(circ, qubit, ang, t):
    circ.add_gate(quantumsim.circuit.RotateZ(qubit, time = t - 0.01, angle = d1q*ang/2))

    circ.add_gate(quantumsim.circuit.RotateY(qubit, time = t, angle = ang))
    circ.add_gate(quantumsim.circuit.OverY(qubit, time = t + 0.0001, theta = epsilon1q*ang, kappa = kap))

    # if chain.index(qubit) == 0:
    #     circ.add_gate(quantumsim.circuit.RotateY(chain[1], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #
    # elif chain.index(qubit) == len(chain) - 1:
    #     circ.add_gate(quantumsim.circuit.RotateY(chain[-2], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #
    # else:
    #     circ.add_gate(quantumsim.circuit.RotateY(chain[chain.index(qubit) - 1], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #     circ.add_gate(quantumsim.circuit.RotateY(chain[chain.index(qubit) + 1], time = t + 0.005, angle = (1+epsilon1q)*ang*RabiRatio1Q))
    #
    #     circ.add_gate(quantumsim.circuit.RotateZ(qubit, time = t + 0.01, angle = d1q*ang/2))

def prep(sdm):
    p = quantumsim.circuit.Circuit()
    p.add_qubit('d0')
    p.add_qubit('d1')
    p.add_qubit('d2')
    p.add_qubit('d3')
    p.add_qubit('d4')
    p.add_qubit('d5')
    p.add_qubit('d6')
    p.add_qubit('d7')
    p.add_qubit('d8')
    p.add_qubit('a')

    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d0', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d1', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d2', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d3', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d4', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d5', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d6', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d7', time = 0, px = pp/3, py = pp/3, pz = pp/3))
    p.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('d8', time = 0, px = pp/3, py = pp/3, pz = pp/3))

    addXX(p, ['d0', 'd1'], 0.01)
    addRX(p, 'd1', -np.pi/2, 1)
    addRY(p, 'd1', np.pi/2, 2)
    addXXm(p, ['d0', 'd2'], 3)
    addRX(p, 'd2', np.pi/2, 4)
    addRY(p, 'd2', np.pi/2, 5)

    addXX(p, ['d3', 'd4'], 0)
    addRX(p, 'd4', -np.pi/2, 1)
    addRY(p, 'd4', np.pi/2, 2)
    addXXm(p, ['d3', 'd5'], 3)
    addRX(p, 'd5', np.pi/2, 4)
    addRY(p, 'd5', np.pi/2, 5)

    addXX(p, ['d6', 'd7'], 0)
    addRX(p, 'd7', -np.pi/2, 1)
    addRY(p, 'd7', np.pi/2, 2)
    addXXm(p, ['d6', 'd8'], 3)
    addRX(p, 'd8', np.pi/2, 4)
    addRY(p, 'd8', np.pi/2, 5)

    p.apply_to(sdm)


def projX0X1X3X4X6X7(sdm, s):
    s1 = quantumsim.circuit.Circuit()
    s1.add_qubit('d0')
    s1.add_qubit('d1')
    s1.add_qubit('d2')
    s1.add_qubit('d3')
    s1.add_qubit('d4')
    s1.add_qubit('d5')
    s1.add_qubit('d6')
    s1.add_qubit('d7')
    s1.add_qubit('d8')
    s1.add_qubit('a')


    addXXm(s1, ['a', 'd0'], 0)
    addRX(s1, 'd0', -np.pi/2, 1)

    addXX(s1, ['a', 'd1'], 2)

    addXXm(s1, ['a', 'd3'], 3)
    addRX(s1, 'd3', -np.pi/2, 4)

    addXX(s1, ['a', 'd4'], 5)

    addXXm(s1, ['a', 'd6'], 6)
    addRX(s1, 'd6', -np.pi/2, 7)

    addXX(s1, ['a', 'd7'], 8)

    s1.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('a', time = 10, px = pm/3, py = pm/3, pz = pm/3))

    s1.apply_to(sdm)
    sdm.project_measurement('a', s)
    temp = sdm.trace()
    sdm.renormalize()

    return temp

def projX1X2X4X5X7X8(sdm, s):
    s2 = quantumsim.circuit.Circuit()
    s2.add_qubit('d0')
    s2.add_qubit('d1')
    s2.add_qubit('d2')
    s2.add_qubit('d3')
    s2.add_qubit('d4')
    s2.add_qubit('d5')
    s2.add_qubit('d6')
    s2.add_qubit('d7')
    s2.add_qubit('d8')
    s2.add_qubit('a')


    addXXm(s2, ['a', 'd1'], 0)

    addXX(s2, ['a', 'd2'], 1)
    addRX(s2, 'd2', np.pi/2, 2)

    addXXm(s2, ['a', 'd3'], 3)

    addXX(s2, ['a', 'd4'], 4)
    addRX(s2, 'd4', np.pi/2, 5)

    addXXm(s2, ['a', 'd7'], 6)

    addXX(s2, ['a', 'd8'], 7)
    addRX(s2, 'd8', np.pi/2, 8)

    s2.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('a', time = 10, px = pm/3, py = pm/3, pz = pm/3))

    s2.apply_to(sdm)
    sdm.project_measurement('a', s)
    temp = sdm.trace()
    sdm.renormalize()

    return temp

def projZ0Z1Z2Z3Z4Z5(sdm, s):
    s3 = quantumsim.circuit.Circuit()
    s3.add_qubit('d0')
    s3.add_qubit('d1')
    s3.add_qubit('d2')
    s3.add_qubit('d3')
    s3.add_qubit('d4')
    s3.add_qubit('d5')
    s3.add_qubit('d6')
    s3.add_qubit('d7')
    s3.add_qubit('d8')
    s3.add_qubit('a')

    addRY(s3, 'd0', np.pi/2, 0)
    addXX(s3, ['a', 'd0'], 1)
    addRX(s3, 'd0', -np.pi/2, 2)
    addRY(s3, 'd0', -np.pi/2, 3)

    addRY(s3, 'd3', np.pi/2, 4)
    addXXm(s3, ['a', 'd3'], 5)

    addRY(s3, 'd1', np.pi/2, 6)
    addXX(s3, ['a', 'd1'], 7)
    addRX(s3, 'd1', -np.pi/2, 8)
    addRY(s3, 'd1', -np.pi/2, 9)

    addRY(s3, 'd4', np.pi/2, 10)
    addXXm(s3, ['a', 'd4'], 11)

    addRY(s3, 'd2', np.pi/2, 12)
    addXX(s3, ['a', 'd2'], 13)
    addRX(s3, 'd2', -np.pi/2, 14)
    addRY(s3, 'd2', -np.pi/2, 15)

    addRY(s3, 'd5', np.pi/2, 16)
    addXXm(s3, ['a', 'd5'], 17)

    s3.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('a', time = 20, px = pm/3, py = pm/3, pz = pm/3))

    s3.apply_to(sdm)
    sdm.project_measurement('a', s)
    temp = sdm.trace()
    sdm.renormalize()

    return temp

def projZ3Z4Z5Z6Z7Z8(sdm, s):
    s4 = quantumsim.circuit.Circuit()
    s4.add_qubit('d0')
    s4.add_qubit('d1')
    s4.add_qubit('d2')
    s4.add_qubit('d3')
    s4.add_qubit('d4')
    s4.add_qubit('d5')
    s4.add_qubit('d6')
    s4.add_qubit('d7')
    s4.add_qubit('d8')
    s4.add_qubit('a')


    addXX(s4, ['a', 'd3'], 0)
    addRY(s4, 'd3', -np.pi/2, 1)

    addRY(s4, 'd6', np.pi/2, 2)
    addXXm(s4, ['a', 'd6'], 3)
    addRX(s4, 'd6', np.pi/2, 4)
    addRY(s4, 'd6', -np.pi/2, 5)

    addXX(s4, ['a', 'd4'], 6)
    addRY(s4, 'd4', -np.pi/2, 7)

    addRY(s4, 'd7', np.pi/2, 8)
    addXXm(s4, ['a', 'd7'], 9)
    addRX(s4, 'd7', np.pi/2, 10)
    addRY(s4, 'd7', -np.pi/2, 11)

    addXX(s4, ['a', 'd5'], 12)
    addRY(s4, 'd5', -np.pi/2, 13)

    addRY(s4, 'd8', np.pi/2, 14)
    addXXm(s4, ['a', 'd8'], 15)
    addRX(s4, 'd8', np.pi/2, 16)
    addRY(s4, 'd8', -np.pi/2, 17)

    s4.add_gate(quantumsim.circuit.AsymmetricDepolarizingNoise('a', time = 20, px = pm/3, py = pm/3, pz = pm/3))

    s4.apply_to(sdm)
    sdm.project_measurement('a', s)
    temp = sdm.trace()
    sdm.renormalize()

    return temp

avgs = [0, 0, 0, 0]

for syn in list(itertools.product([0,1], repeat = 4)):
    epsilon = eps
    sdm = SparseDM(['d0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'a'])

    prep(sdm)

    prob = 1
    prob = prob*projX0X1X3X4X6X7(sdm, syn[0])
    prob = prob*projX1X2X4X5X7X8(sdm, syn[1])
    prob = prob*projZ0Z1Z2Z3Z4Z5(sdm, syn[2])
    prob = prob*projZ3Z4Z5Z6Z7Z8(sdm, syn[3])

    print(''.join([str(s) for s in syn]),': ', prob)

    for i in range(4):
        avgs[i] += prob*syn[i]


print(avgs)
