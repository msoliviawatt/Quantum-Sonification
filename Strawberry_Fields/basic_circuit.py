import strawberryfields as sf
import pennylane as qml
import numpy as np
from strawberryfields import ops # assuming this means operations(?)


# new program with 3 modes
prog = sf.program(3)

# with statement used to populate program with quantum operations
# program_name.context uesd within with stateen to reutrn a q, which
# is a representation of the quantum registers (qumodes or modes)
with prog.context as q:
    ops.Sgate(0.54) | q[0]
    ops.Sgate(0.54) | q[1]
    ops.Sgate(0.54) | q[2]
    ops.BSgate(0.43, 0.1) | (q[0], q[2])
    ops.BSgate(0.43, 0.1) | (q[1], q[2])
    ops.MeasureFock() | q

# program.print() will show the contents of a program
# program.draw_circuit() will show the qcircuit

# enginer must be initialized before simulating
# this code iniitalizes a fock backend with a fock cutoff dimension of 5
eng = sf.Engine("fock", backend_options={"cuttoff_dim": 5})

# types of backends
#
# fock:     fock basis with numerical error due to truncation
#           increased cutoff = higher accuracy but more memory consumption
#
# gaussian: represents quantum state as a guassian and operations as quantum
#           operations. numerically exact, consumes less memory, less computationally intensive
#           than fock. however, does not represent non-gaussian operations and states which fock does
# 
# bosonic:  simulates states that can be represented as a linear combination of gaussian functions
#           in phase space. provides succinct descriptions of gaussian states AND non-gaussian states. 
#           very efficient
#
# tf:       tensorflow... fock basis representation but allows for optimization 
#           and backpropogation with tensorflow

# simulate the program
result = eng.run(prog)

# get information from the terminal commands:
# print(result.state)
# state = result.state           # trace of the sate
# state.trace()
# state.dm().shape               # density matrix