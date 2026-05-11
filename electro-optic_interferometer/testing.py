import numpy as np
import matplotlib.pyplot as plt

from models import RabiModel, MachZehnderModel, PhaseShifterModel, ResonatorModel

def main():
    fig, axes = plt.subplots(2, 2, figsize = (10, 6))
    plot_1 = axes[0, 0]
    plot_2 = axes[0, 1]
    plot_3 = axes[1, 0]
    plot_4 = axes[1, 1]
    # test rabi
    t = np.linspace(0, 4, 1000)
    rabi = RabiModel()

    omega = 6.0
    detuning = 0.0
    prob_g, prob_e = rabi.probabilities(t, omega, detuning)

    plot_1.plot(t, prob_g, label = "Ground State Probability")
    plot_1.plot(t, prob_e, label = "Excited State Probability")
    plot_1.set_xlabel("Time")
    plot_1.set_ylabel("Probability")
    plot_1.set_title("Rabi Oscillations")
    plot_1.legend()
    plot_1.grid()

    # test mzi
    mzi = MachZehnderModel()

    phase = np.linspace(0, 2 * np.pi, 1000)
    prob_0, prob_1 = mzi.output_probabilities(phase)

    plot_2.plot(phase, prob_0, label = "Output 0")
    plot_2.plot(phase, prob_1, label = "Output 1")
    plot_2.set_xlabel("Phase")
    plot_2.set_ylabel("Probabilitiy")
    plot_2.set_title("Mach Zehnder Interferometer")
    plot_2.legend()
    plot_2.grid()

    # test phase shifter
    v_for_pi = 5.0
    phase_shifter = PhaseShifterModel(v_for_pi)
    voltage = np.linspace(0, 10, 1000)
    phase_from_v = phase_shifter.phase_from_voltage(voltage)

    plot_3.plot(voltage, phase_from_v)
    plot_3.set_xlabel("Voltage")
    plot_3.set_ylabel("Phase")
    plot_3.set_title("Voltage to Optical Phase")
    plot_3.grid()

    # test resonator
    resonator = ResonatorModel()
    drive_frequency = np.linspace(1, 30, 1000)
    resonance_frequency = 10.0
    q_factor = 20
    gain = resonator.enhancement(drive_frequency, resonance_frequency, q_factor)

    plot_4.plot(drive_frequency, gain)
    plot_4.set_xlabel("Drive Frequency")
    plot_4.set_ylabel("Enhancement")
    plot_4.set_title("Mechanical Resonance Enhancement")
    plot_4.grid()

    # show the plots
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()