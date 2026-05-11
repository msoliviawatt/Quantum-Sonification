import sounddevice as sd
import numpy as np

class Audio:

    def __init__(self, sample_rate = 44100):
        self.sample_rate = sample_rate

        self.phase_g = 0.0
        self.phase_e = 0.0

        # starting frequencies
        self.freq_groud = 220.0
        self.freq_excited = 330.0

        self.volume = 0.2
        self.vibrato_depth = 2.0
        self.vibrato_rate = 5.0

    def reset_phases(self):
        self.phase_g = 0.0
        self.phase_e = 0.0

    def _oscillator(self, frequency, frames, phase_start):
        
        phase_increase = 2 * np.pi * frequency / self.sample_rate
        phase = phase_start + np.cumsum(np.full(frames, phase_increase))

        signal = np.sin(phase)
        phase_end = phase[-1] % (2 * np.pi)

        return signal, phase_end
    
    def audio_rabi(self, prob_g, prob_e):

        frames = len(prob_g)

        ground_audio, self.phase_g = self._oscillator(self.freq_groud, frames, self.phase_g)
        excited_audio, self.phase_e = self._oscillator(self.freq_excited, frames, self.phase_e)

        mono = prob_g * ground_audio + prob_e * excited_audio
        mono = np.tanh(1.2 * mono)

        width = 0.15 + 0.35 * np.abs(prob_e - prob_g)

        left = mono * (1.0 - width)
        right = mono * (1.0 + width)

        stereo = np.column_stack((left, right))
        stereo *= self.volume

        return stereo.astype(np.float32)
    
    def audio_mzi(self, prob_0, prob_1, base_frequency = 440.0):
        frames = len(prob_0)

        tone, self.phase_g = self._oscillator(base_frequency, frames, self.phase_g)

        left = tone * np.sqrt(prob_0)
        right = tone * np.sqrt(prob_1)

        stereo = np.column_stack((left, right))
        stereo *= self.volume

        return stereo.astype(np.float32)
    
    def audio_resonance(self, gain, base_frequency = 220.0):
        frames = len(gain)

        tone, self.phase_g = self._oscillator(base_frequency, frames, self.phase_g)

        gain_norm = gain / np.max(np.abs(gain))

        mono = tone * gain_norm
        mono = np.tanh(1.2 * mono)

        stereo = np.column_stack((mono, mono))
        stereo *= self.volume

        return stereo.astype(np.float32)


    def generate_audio(self):
        pass