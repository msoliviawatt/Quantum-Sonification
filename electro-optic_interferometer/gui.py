import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models import RabiModel, MachZehnderModel, PhaseShifterModel, ResonatorModel
from audio import Audio

class GUI:
    def __init__(self):        
        self.sample_rate = 44100
        self.blocksize = 512

        self.lock = threading.Lock()
        self.running = False
        self.t0 = 0.0

        # models
        self.rabi = RabiModel()
        self.mzi = MachZehnderModel()
        self.phase_shifter = PhaseShifterModel(v_pi = 5.0)
        self.resonator = ResonatorModel()
        self.audio = Audio(sample_rate=self.sample_rate)

        # mode
        self.mode = "Rabi"

        # params
        self.omega = 6.0
        self.detuning = 0.0
        self.voltage = 2.5
        self.drive_freq = 10.0
        self.resonance_freq = 10.0
        self.q_factor = 20.0

        self.stream = None

        self._build_gui()
        self._update_plot()


    def run(self):
        self.root.mainloop()

    def on_close(self):
        self.running = False

        try:
            if (self.stream is not None):
                self.stream.stop()
                self.stream.close()
        finally:
            self.root.destroy()

    def _build_gui(self):
        self.root = tk.Tk()
        self.root.title("Electro-Optic Interferomter")
        self.root.geometry("1000x750")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        outer = ttk.Frame(self.root, padding = 12)
        outer.pack(fill = "both", expand = True)

        title = ttk.Label(
            outer,
            text = "Electro-Optic Interferometer",
            font = ("Segoe UI", 16, "bold")
        )
        title.pack(anchor = "w", pady = (0, 10))

        # drowpdown menu for mode!
        controls = ttk.Frame(outer)
        controls.pack(fill = "x", pady = (0, 10))

        ttk.Label(controls, text = "Mode").grid(row = 0, column = 0, sticky = "w")
        self.mode_var = tk.StringVar(value=self.mode)
        mode_box = ttk.Combobox(
            controls,
            textvariable = self.mode_var,
            values = ["Rabi", "Mach-Zehnder", "Resonant MZI"],
            state = "readonly"
        )
        mode_box.grid(row = 0, column = 1, sticky = "ew", padx = 8)
        mode_box.bind("<<ComboboxSelected>>", self.on_slider_change)

        # rabi frequency
        self.omega_var = tk.DoubleVar(value=self.omega)
        self._add_slider(controls, "Rabi frequency Ω", self.omega_var, 0.1, 20.0, 1)

        # detuning
        self.detuning_var = tk.DoubleVar(value=self.detuning)
        self._add_slider(controls, "Detuning Δ", self.detuning_var, -20.0, 20.0, 2)

        # voltage
        self.voltage_var = tk.DoubleVar(value=self.voltage)
        self._add_slider(controls, "Voltage V", self.voltage_var, 0.0, 10.0, 3)

        # drive frequency
        self.drive_freq_var = tk.DoubleVar(value=self.drive_freq)
        self._add_slider(controls, "Drive frequency", self.drive_freq_var, 1.0, 30.0, 4)

        # resonance frequency
        self.resonance_freq_var = tk.DoubleVar(value=self.resonance_freq)
        self._add_slider(controls, "Resonance frequency", self.resonance_freq_var, 1.0, 30.0, 5)

        # Q factor
        self.q_factor_var = tk.DoubleVar(value=self.q_factor)
        self._add_slider(controls, "Q factor", self.q_factor_var, 1.0, 80.0, 6)

        controls.columnconfigure(1, weight=1)


        # buttons
        button_row = ttk.Frame(outer)
        button_row.pack(fill="x", pady=(0, 10))

        ttk.Button(button_row, text="Start", command=self.start_audio).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Stop", command=self.stop_audio).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Reset", command=self.reset).pack(side="left")

        self.status_var = tk.StringVar(value="Stopped")
        ttk.Label(button_row, textvariable=self.status_var).pack(side="right")

        # plot
        fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.grid(True, alpha=0.3)

        self.line1, = self.ax.plot([], [], label="Signal 1")
        self.line2, = self.ax.plot([], [], label="Signal 2")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(fig, master=outer)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _update_plot(self):
        with self.lock:
            mode = self.mode
            omega = self.omega
            detuning = self.detuning
            voltage = self.voltage
            drive_freq = self.drive_freq
            resonance_freq = self.resonance_freq
            q_factor = self.q_factor

        t = np.linspace(0, 4, 1000)

        if mode == "Rabi":
            y1, y2 = self.rabi.probabilities(t, omega, detuning)
            x = t
            label1 = "Prob_ground(t)"
            label2 = "Prob_excited(t)"
            title = "Rabi Oscillations"

        elif mode == "Mach-Zehnder":
            phase = np.linspace(0, 2 * np.pi, 1000)
            y1, y2 = self.mzi.output_probabilities(phase)
            x = phase
            label1 = "Output 0"
            label2 = "Output 1"
            title = "Mach-Zehnder Interference"

        else:
            voltage_t = voltage * np.sin(2 * np.pi * drive_freq * t)
            gain = self.resonator.enhancement(drive_freq, resonance_freq, q_factor)
            phase_t = self.phase_shifter.phase_from_voltage(gain * voltage_t)
            y1, y2 = self.mzi.output_probabilities(phase_t)
            x = t
            label1 = "Output 0"
            label2 = "Output 1"
            title = f"Resonant MZI, gain = {gain:.2f}"

        self.line1.set_data(x, y1)
        self.line2.set_data(x, y2)

        self.line1.set_label(label1)
        self.line2.set_label(label2)

        self.ax.clear()
        self.ax.plot(x, y1, label = label1)
        self.ax.plot(x, y2, label = label2)
        self.ax.set_title(title)
        self.ax.set_xlabel("Time" if mode != "Mach-Zehnder" else "Phase")
        self.ax.set_ylabel("Probability")
        self.ax.grid(True, alpha = 0.3)
        self.ax.legend()
        self.canvas.draw_idle()

        self.root.after(100, self._update_plot)

    def _add_slider(self, parent, label, variable, min_val, max_val, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")

        slider = ttk.Scale(
            parent,
            from_=min_val,
            to=max_val,
            variable=variable,
            orient="horizontal",
            command=self.on_slider_change
        )
        slider.grid(row=row, column=1, sticky="ew", padx=8)

        entry_var = tk.StringVar(value=f"{variable.get():.2f}")

        entry = ttk.Entry(parent, textvariable=entry_var, width=8)
        entry.grid(row=row, column=2, sticky="w")

        variable.entry_var = entry_var
        variable.min_val = min_val
        variable.max_val = max_val

        entry.bind("<Return>", lambda event, v=variable: self.on_entry_change(v))
        entry.bind("<FocusOut>", lambda event, v=variable: self.on_entry_change(v))

    def on_slider_change(self, _event=None):
        with self.lock:
            self.mode = self.mode_var.get()
            self.omega = float(self.omega_var.get())
            self.detuning = float(self.detuning_var.get())
            self.voltage = float(self.voltage_var.get())
            self.drive_freq = float(self.drive_freq_var.get())
            self.resonance_freq = float(self.resonance_freq_var.get())
            self.q_factor = float(self.q_factor_var.get())

        for var in [
            self.omega_var,
            self.detuning_var,
            self.voltage_var,
            self.drive_freq_var,
            self.resonance_freq_var,
            self.q_factor_var,
        ]:
            var.entry_var.set(f"{var.get():.2f}")

    def on_entry_change(self, variable):
        try:
            value = float(variable.entry_var.get())
        except ValueError:
            variable.entry_var.set(f"{variable.get():.2f}")
            return

        value = max(variable.min_val, min(variable.max_val, value))

        variable.set(value)

        self.on_slider_change()

    def reset(self):
        with self.lock:
            self.t0 = 0.0
        self.audio.reset_phases()

    def compute(self, frames):
        with self.lock:
            mode = self.mode
            omega = self.omega
            detuning = self.detuning
            voltage = self.voltage
            drive_freq = self.drive_freq
            resonance_freq = self.resonance_freq
            q_factor = self.q_factor

            t = self.t0 + np.arange(frames) / self.sample_rate
            self.t0 = t[-1] + 1.0 / self.sample_rate

        if mode == "Rabi":
            pg, pe = self.rabi.probabilities(t, omega, detuning)
            audio = self.audio.audio_rabi(pg, pe)
            return audio

        if mode == "Mach-Zehnder":
            phase = self.phase_shifter.phase_from_voltage(voltage)
            p0, p1 = self.mzi.output_probabilities(phase)
            p0 = np.full(frames, p0)
            p1 = np.full(frames, p1)
            audio = self.audio.audio_mzi(p0, p1)
            return audio

        if mode == "Resonant MZI":
            gain = self.resonator.enhancement(drive_freq, resonance_freq, q_factor)

            voltage_t = voltage * gain * np.sin(2 * np.pi * drive_freq * t)
            phase_t = self.phase_shifter.phase_from_voltage(voltage_t)

            p0, p1 = self.mzi.output_probabilities(phase_t)
            audio = self.audio.audio_mzi(p0, p1)
            return audio

        return np.zeros((frames, 2), dtype=np.float32)
    
    def audio_callback(self, outdata, frames, _time_info, status):
        if status:
            print(status)

        if not self.running:
            outdata.fill(0)
            return

        outdata[:] = self.compute(frames)

    def start_audio(self):
        if self.running:
            return

        self.running = True

        if self.stream is None:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.blocksize,
                channels=2,
                dtype="float32",
                callback=self.audio_callback
            )
            self.stream.start()

        self.status_var.set("Running")

    def stop_audio(self):
        self.running = False
        self.status_var.set("Stopped")