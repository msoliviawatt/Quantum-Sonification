import numpy as np

class RabiModel:
    def probabilities(self, t, omega, detuning):
        omega_eff = np.sqrt(omega**2 + detuning**2)

        if (omega_eff < 1e-12):
            prob_excited = np.zeros_like(t)
        else:
            contrast = omega**2 / omega_eff**2
            prob_excited = contrast * np.sin(0.5 * omega_eff * t) **2

        prob_ground = 1.0 - prob_excited

        return prob_ground, prob_excited
    
class MachZehnderModel:
    def output_probabilities(self, phase):
        prob_0 = np.sin(phase / 2) ** 2
        prob_1 = np.cos(phase / 2) **2

        return prob_0, prob_1
    

class PhaseShifterModel:
    # v_pi is the voltage necessary to produce a phase shift of pi
    def __init__(self, v_pi):
        self.v_pi = v_pi

    def phase_from_voltage(self, voltage):
        phase = np.pi * voltage / self.v_pi
        return phase
    
class ResonatorModel:
    def enhancement(self, drive_freq, resonance_freq, q_factor):
        ratio = drive_freq / resonance_freq
        denominator = np.sqrt((1 - ratio**2) **2 + (ratio / q_factor) **2)
        gain = 1 / denominator
        return gain
