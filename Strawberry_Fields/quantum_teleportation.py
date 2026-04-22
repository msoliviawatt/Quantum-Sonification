################################################################
# quantum teleportation protocol but with photons for CVQC
################################################################
# imports strawverry fields for engine and backend
import strawverryfields as sf

# imports all cv gates into the namespace
from strawberryfields.ops import *

import numpy as np
from numpy import pi, sqrt

# random seed
np.random.seed(42)

# note: sf uses h_bar = 2, but this can be changed by setting ```sf.hbar```
# this will modify the application of the Xgate and Zgate as well as the homodyne measurement

# instantiate program class
#
# the program class looks like:
#           sf.Program(num_susbsystems, name = None)
#
# num_susbsystems is number of modes we want to initialize
# name is optional
prog = sf.Program(3)

# let's say we want to teleport the coherent state alpha = 1 + j0.5
alpha = 1 + 0.5j
r = np.abs(alpha)
phi = np.angle(alpha)

with prog.context as q:
    # initial states
    Coherent(r, phi) | q[0]
    Squeezed(-2) | q[1]
    Squeezed(2) | q[2]

    # gates
    BS = BSgate(pi/4, pi)
    BS | (q[1], q[2])
    BS | (q[0], q[1])

    # homodyne measurements
    MeasureX | q[0]
    MeasureP |q[1]

    # displacement gates for qubit 2 depend on the homodyne measurements
    Xgate(sqrt(2), * q[0].par) | q[2]
    Zgate(-sqrt(2), * q[1].par) | q[2]
