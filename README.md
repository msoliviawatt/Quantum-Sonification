# Sonification-of-Quantum-Photonic-Circuits
This project workspace currently has three working simulations -- the electro-optic interferometer, the Mach Zehnder interferomter, and the rabi oscillations app. The latter two were eventually implemented into the electro-optic interferometer, so I would recommend just focusing there (i.e. the `electro-optic_interferometer` directory). 

## Setup
Make sure you have initialized a Python virtual environment.

Run the following command to install the necessary modules within the venv.
```
python3 -m pip install -r requirements.txt
```

The main simulation to run with this repository is the electro-optic interferometer. There is a README in that directory, but those same contents are also below. 

The electro-optic interferometer app has three modes: Rabi, Mach-Zehnder (MZI), and Resonant MZI. Each mode represents a different physical subsystem involved in the complete electro-optic interferometer model. The simulation architecture was divided into separate models, audio synthesis, and graphical interface layers in order to distinguish the underlying physical calculations from the visualization and sonification components. In all operating modes, the user is able to modify system parameters in real-time through sliders and numerical entry boxes. The resulting behavior is simultaneously visualized through dynamic plots and converted into audio using a real-time sound synthesis engine.

## Instructions
You will need to run this on Windows for the GUI interface to work. Make sure you have the necessary dependencies installed and a virtual environment set up if you are using one. 

To run a file, use `py .\[filename].py`. For example,
```
py .\testing.py 
```

Or
```
py .\main.py
```

The syntax might vary if you are using a different version of Python.

You should also be able to press the "Run Code" button at the top of the file if using Visual Studio Code.

The main file you will want to run is `main.py`. This will open the GUI where you can experiment with changing the rabi frequency, detuning, voltage, drive frequency, resonance frequency, and Q factor. 

### Rabi Mode
In the Rabi Oscillations mode, the excited-state population is computed using

$P_e(t) = \frac{\Omega^2}{\Omega^2 + \Delta^2}\sin^2\left(\frac{\Omega_{\text{eff}} t}{2} \right)$,

where

$\Omega_{\text{eff}} = \sqrt{\Omega^2 + \Delta^2}$

Here, $\Omega$ is the Rabi frequency and $\Delta$ is the detuning. The ground-state probability is then computed using

$P_g(t) = 1 - P_e(t)$

The Rabi frequency controls how rapidly the populations oscillate, while the detuning controls how efficiently population transfer occurs. At zero detuning, the system undergoes complete oscillation between the two states. As the detuning
increases, the oscillation amplitude decreases.

Within the simulation, the two populations are mapped to separate synthesized audio tones. The amplitudes of the tones are continuously weighted according to the probabilities $\text{Prob}\_{\text{ground}}(t)$ and $\text{Prob}\_{\text{excited}}(t)$, allowing us to hear the changing state populations in real time. Slow Rabi frequencies produce gradual oscillatory audio behavior, while larger frequencies produce more rapid modulation.

### MZI Mode
This mode is the core optical interference behavior of the electro-optic interferometer. The output probabilities are computed using

$P_0 = \sin^2\left(\frac{\Delta \phi}{2}\right)$ and $P_1 =\cos^2\left(\frac{\Delta \phi}{2}\right),$

where $\Delta \phi$ is the optical phase difference induced by the phase shifter. The phase shift is generated from the applied voltage according to $\phi(V) = \pi \frac{V}{V_{\pi}}$, where $V_{\pi}$ is the voltage required to produce a $\pi$ phase shift.

In this mode, changing the voltage directly changes the optical phase and thus redistributes the optical power between the two output ports. Constructive interference in one port results in destructive interference in the other. The simulation visualizes this redistribution through the plotted output probabilities. Simultaneously, the probabilities are mapped to the amplitudes of left and right stereo audio channels. As the interference pattern changes, we should hear the sound shift between channels, creating an audible representation of optical interference. Small voltage values produce weak interference modulation, while larger voltages generate stronger transitions between constructive and destructive interference.

### Resonant MZI Mode
This resonance mode extends the Mach-Zehnder interferometer model by incorporating a mechanical resonator, which behaves as a driven mechanical oscillator possessing a natural resonant frequency $\omega_0 = \sqrt{\frac{k}{m}}$, where $k$ is the effective stiffness and $m$ is the effective mass of the mechanical structure. 

An externally applied sinusoidal voltage $V(t) = V_0\sin(2\pi f_{\text{drive}} t)$ drives the resonator. The resonator response depends strongly on the relationship between the drive frequency and the resonant frequency.

The resonance enhancement is modeled using

$G(\omega) = \frac{1}{\sqrt{\left(1 -\left(\frac{\omega}{\omega_0}\right)^2\right)^2 +
    \left(\frac{\omega}{Q\omega_0}\right)^2}},$

where $Q$ is the quality factor of the resonator. The effective voltage applied to the phase shifter becomes

$V_{\text{eff}}(t) = G(\omega_{\text{drive}}) V(t).$

Physically, this means that the resonator amplifies the phase modulation most strongly when the drive frequency approaches the resonant frequency. The simulation is meant to show how resonance enhancement dramatically changes the interference behavior of the interferometer. Near resonance, even relatively small voltages can produce large optical phase oscillations, resulting in significantly stronger interference modulation.

The simulation allows for the change of four parameters:

- Voltage
- Drive frequency
- Resonance frequency
- Quality factor

Changing the drive frequency controls how rapidly the system is externally driven. Changing the resonance frequency changes the natural frequency at which the system responds most strongly. Adjusting the quality factor modifies the sharpness and strength of the resonance peak. When the drive frequency closely matches the resonance frequency, the system exhibits maximum amplification. In the audio output, this produces stronger modulation depth, more dramatic stereo motion, and significantly enhanced oscillatory behavior. When the frequencies are far apart, the modulation becomes weaker and the sound correspondingly becomes more subdued.

## Notes
To save a .ipynb file as a PDF, use the following command.
```
jupyter nbconvert --to webpdf --allow-chromium-download [local_file_path]
```