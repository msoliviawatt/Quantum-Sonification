import numpy as np
import matplotlib.pyplot as plt

from models import RabiModel, MachZehnderModel, PhaseShifterModel, ResonatorMode

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

if __name__ == "__main__":
    main()