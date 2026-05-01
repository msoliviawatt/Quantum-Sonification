import numpy as np
import matplotlib.pyplot as plt

from models import RabiModel, MachZehnderModel, PhaseShifterModel, ResonatorModel

def main():
    # test rabi
    t = np.linspace(0, 4, 1000)
    rabi = RabiModel()

    prob_g, prob_e = rabi.probabilities(t, 6.0, 0.0)

    plt.figure(figsize=(10, 6))
    plt.plot(t, prob_g, label = "Ground State Probability")
    plt.plot(t, prob_e, label = "Excited State Probability")
    plt.xlabel("Time")
    plt.ylabel("Probability")
    plt.title("Rabi Oscillations")
    plt.legend()
    plt.grid()
    plt.show()

    # test mzi
    mzi = MachZehnderModel()

    phase = np.linspace(0, 2 * np.pi, 1000)
    prob_0, prob_1 = mzi.output_probabilities(phase)

    plt.figure(figsize=(10, 6))
    plt.plot(phase, prob_0, label = "Output 0")
    plt.plot(phase, prob_1, label = "Output 1")
    plt.xlabel("Phase")
    plt.ylabel("Probabilitiy")
    plt.title("Mach Zehnder Interferometer")
    plt.legend()
    plt.grid()
    plt.show()

    # test phase shifter
    phase_shifter = PhaseShifterModel(5.0)
    voltage = np.linspace(0, 10, 1000)
    phase_from_v = phase_shifter.phase_from_voltage(voltage)

    plt.figure(figsize=(10, 6))
    plt.plot(voltage, phase_from_v)
    plt.xlabel("Voltage")
    plt.ylabel("Phase")
    plt.title("Voltage to Optical Phase")
    plt.grid()
    plt.show()

    # test resonator
    resonator = ResonatorModel()
    drive_frequency = np.linspace(1, 30, 1000)
    resonance_frequency = 10.0
    gain = resonator.enhancement(drive_frequency, resonance_frequency, 20)

    plt.figure(figsize=(10, 6))
    plt.plot(drive_frequency, gain)
    plt.xlabel("Drive Frequency")
    plt.ylabel("Enhancement")
    plt.title("Mechanical Resonance Enhancement")
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()