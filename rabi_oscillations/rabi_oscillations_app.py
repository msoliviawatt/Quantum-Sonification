# threading module so that the gui and audio callback don't try to edit the same variable at the same time
import threading

# for calculations and general numerical stuff 
import numpy as np

# library that sends audio samples to speakers
import sounddevice as sd

# gui -- tk for window, ttk for widgets
import tkinter as tk
from tkinter import ttk

# allows matplotlib plot inside of tkinter window
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# self-explanitory
from matplotlib.figure import Figure


class RabiSonifier:
    ##############################################
    # on init
    ##############################################
    def __init__(self):
        self.sample_rate = 44100
        self.blocksize = 512

        # shared state
        self.lock = threading.Lock()
        self.running = False # whether audio should be playing

        # physical params
        self.omega = 6.0 # starting rabi frequency
        self.detuning = 0.0 # delta omega
        self.master_volume = 0.22 

        # audio params 
        self.f_ground = 220.0
        self.f_excited = 330.0
        self.vibrato_depth = 2.0
        self.vibrato_rate = 5.0

        # time
        self.t0 = 0.0 # current global time in seconds

        # phase components of ground and excited states
        self.phase_g1 = 0.0
        self.phase_g2 = 0.0
        self.phase_e1 = 0.0
        self.phase_e2 = 0.0

        # plot params
        self.plot_duration = 4.0 # number of seconds shown on the plot
        self.plot_points = 1200
        self.last_plot_pe = None
        self.last_plot_pg = None
        self.last_plot_t = None

        self.stream = None

        self._build_gui()
        self._update_plot()

    ##############################################
    # creates the interface
    ##############################################
    def _build_gui(self):
        self.root = tk.Tk()
        self.root.title("Interactive Rabi Oscillation Sonification")
        self.root.geometry("980x720")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # outer frame
        outer = ttk.Frame(self.root, padding = 12)
        outer.pack(fill = "both", expand = True)

        # controls frame
        controls = ttk.Frame(outer)
        controls.pack(fill = "x", pady = (0, 10))

        # title label
        title = ttk.Label(
            controls,
            text = "Interactive Rabi Oscillation Sonification",
            font = ("Segoe UI", 16, "bold")
        )
        title.grid(row = 0, column = 0, columnspan = 4, sticky = "w", pady = (0, 8))

        # status display
        self.status_var = tk.StringVar(value = "Stopped")
        status = ttk.Label(controls, textvariable = self.status_var)
        status.grid(row = 0, column = 4, sticky = "e")

        # omega slider
        ttk.Label(controls, text = "Rabi frequency Ω").grid(row = 1, column = 0, sticky = "w")
        self.omega_var = tk.DoubleVar(value = self.omega)
        self.omega_scale = ttk.Scale(
            controls, from_ = 0.1, to = 20.0, variable = self.omega_var,
            orient = "horizontal", command = self.on_slider_change
        )
        self.omega_scale.grid(row = 1, column = 1, sticky = "ew", padx = 8)
        self.omega_value = ttk.Label(controls, text = f"{self.omega:.2f}")
        self.omega_value.grid(row = 1, column = 2, sticky = "w")

        # detuning slider
        ttk.Label(controls, text = "Detuning Δω").grid(row = 2, column = 0, sticky = "w")
        self.detuning_var = tk.DoubleVar(value = self.detuning)
        self.detuning_scale = ttk.Scale(
            controls, from_ = -20.0, to = 20.0, variable = self.detuning_var,
            orient = "horizontal", command = self.on_slider_change
        )
        self.detuning_scale.grid(row = 2, column = 1, sticky = "ew", padx = 8)
        self.detuning_value = ttk.Label(controls, text = f"{self.detuning:.2f}")
        self.detuning_value.grid(row = 2, column = 2, sticky = "w")

        # bolume slider
        ttk.Label(controls, text = "Volume").grid(row = 3, column = 0, sticky = "w")
        self.volume_var = tk.DoubleVar(value = self.master_volume)
        self.volume_scale = ttk.Scale(
            controls, from_ = 0.01, to = 0.6, variable = self.volume_var,
            orient = "horizontal", command = self.on_slider_change
        )
        self.volume_scale.grid(row = 3, column = 1, sticky = "ew", padx = 8)
        self.volume_value = ttk.Label(controls, text = f"{self.master_volume:.2f}")
        self.volume_value.grid(row = 3, column = 2, sticky = "w")

        # buttons
        button_row = ttk.Frame(controls)
        button_row.grid(row = 4, column = 0, columnspan = 5, sticky = "w", pady = (10, 0))

        self.start_button = ttk.Button(button_row, text = "Start", command = self.start_audio)
        self.start_button.pack(side = "left", padx = (0, 8))

        self.stop_button = ttk.Button(button_row, text = "Stop", command = self.stop_audio)
        self.stop_button.pack(side = "left", padx = (0, 8))

        self.reset_button = ttk.Button(button_row, text = "Reset phase", command = self.reset_time)
        self.reset_button.pack(side = "left")

        # grid resizing
        controls.columnconfigure(1, weight = 1)
        controls.columnconfigure(4, weight = 1)

        # info box
        info = ttk.Label(
            outer,
            text = (
                "Ground-state and excited-state probabilities are mapped to two blended tones.\n"
                "Ω changes oscillation rate. Δω changes both the rate and contrast."
            ),
            justify = "left"
        )
        info.pack(anchor = "w", pady = (0, 10))

        # figure
        fig = Figure(figsize = (10, 5), dpi = 100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Spin Probabilities vs Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Probability")
        self.ax.set_ylim(-0.02, 1.02)
        self.ax.grid(True, alpha = 0.3)

        self.line_pg, = self.ax.plot([], [], label = "P_g(t)")
        self.line_pe, = self.ax.plot([], [], label = "P_e(t)")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(fig, master = outer)
        self.canvas.get_tk_widget().pack(fill = "both", expand = True)


    ##############################################
    # slider change behavior
    ##############################################
    def on_slider_change(self, _event = None):
        with self.lock:
            self.omega = float(self.omega_var.get())
            self.detuning = float(self.detuning_var.get())
            self.master_volume = float(self.volume_var.get())

        self.omega_value.config(text = f"{self.omega:.2f}")
        self.detuning_value.config(text = f"{self.detuning:.2f}")
        self.volume_value.config(text = f"{self.master_volume:.2f}")

    ##############################################
    # time reset
    ##############################################
    def reset_time(self):
        with self.lock:
            self.t0 = 0.0
            self.phase_g1 = 0.0
            self.phase_g2 = 0.0
            self.phase_e1 = 0.0
            self.phase_e2 = 0.0

    @staticmethod
    ##############################################
    # probabilities/populations
    ##############################################
    def probabilities(t, omega, detuning):
        omega_eff = np.sqrt(omega**2 + detuning**2)
        if omega_eff < 1e-12:
            pe = np.zeros_like(t)
        else:
            contrast = (omega**2) / (omega_eff**2)
            pe = contrast * np.sin(0.5 * omega_eff * t)**2
        pg = 1.0 - pe
        return pg, pe

    ##############################################
    # sound synthesis
    ##############################################
    def synth_block(self, frames):
        with self.lock:
            omega = self.omega
            detuning = self.detuning
            volume = self.master_volume

            t = self.t0 + np.arange(frames) / self.sample_rate
            self.t0 = t[-1] + 1.0 / self.sample_rate

            pg, pe = self.probabilities(t, omega, detuning)

            # slight vibrato tied to probability dynamics
            vib = self.vibrato_depth * np.sin(2 * np.pi * self.vibrato_rate * t)

            # this is so that the two tones move in opposite directions
            fg = self.f_ground + 0.4 * detuning + vib
            fe = self.f_excited + 0.7 * detuning - vib

            # synthesis (builds the sine wave incrementally instead of recomputing every time)
            g1_inc = 2 * np.pi * fg / self.sample_rate
            g2_inc = 2 * np.pi * (2.0 * fg) / self.sample_rate
            e1_inc = 2 * np.pi * fe / self.sample_rate
            e2_inc = 2 * np.pi * (1.5 * fe) / self.sample_rate

            phase_g1 = self.phase_g1 + np.cumsum(g1_inc)
            phase_g2 = self.phase_g2 + np.cumsum(g2_inc)
            phase_e1 = self.phase_e1 + np.cumsum(e1_inc)
            phase_e2 = self.phase_e2 + np.cumsum(e2_inc)

            self.phase_g1 = float(phase_g1[-1] % (2 * np.pi))
            self.phase_g2 = float(phase_g2[-1] % (2 * np.pi))
            self.phase_e1 = float(phase_e1[-1] % (2 * np.pi))
            self.phase_e2 = float(phase_e2[-1] % (2 * np.pi))

        # textured voices (main tone + harmonics + extra for character)
        ground_voice = (
            0.75 * np.sin(phase_g1) +
            0.20 * np.sin(phase_g2 + 0.15) +
            0.08 * np.sin(3.0 * phase_g1 + 0.4)
        )

        excited_voice = (
            0.65 * np.sin(phase_e1) +
            0.25 * np.sin(phase_e2 + 0.3) +
            0.10 * np.sin(2.5 * phase_e1 + 0.7)
        )

        # compresses loud peaks and prevents clipping
        # tanh because small values become linear, and larger ones flatten
        mono = pg * ground_voice + pe * excited_voice
        mono = np.tanh(1.35 * mono)

        # stereo width from probability imbalance (i.e. how wide the sound is)
        width = 0.15 + 0.35 * np.abs(pe - pg)

        # apply width to audio channels
        left = mono * (1.0 - width)
        right = mono * (1.0 + width)

        # combine to stereo sginal
        stereo = np.column_stack((left, right))
        stereo *= volume

        # save plot arrays occasionally from current parameters
        with self.lock:
            t_plot = np.linspace(max(0.0, self.t0 - self.plot_duration),
                                 max(self.plot_duration, self.t0),
                                 self.plot_points)
            pg_plot, pe_plot = self.probabilities(
                t_plot, self.omega, self.detuning
            )
            self.last_plot_t = t_plot
            self.last_plot_pg = pg_plot
            self.last_plot_pe = pe_plot

        return stereo.astype(np.float32)


    ##############################################
    # audio callback
    ##############################################
    def audio_callback(self, outdata, frames, _time_info, status):
        if status:
            print(status)
        if not self.running:
            outdata.fill ( 0)
            return
        outdata[:] = self.synth_block(frames)


    ##############################################
    # run audio
    ##############################################
    def start_audio(self):
        if self.running:
            return
        self.running = True

        if self.stream is None:
            self.stream = sd.OutputStream(
                samplerate = self.sample_rate,
                blocksize = self.blocksize,
                channels = 2,
                dtype = "float32",
                callback = self.audio_callback
            )
            self.stream.start()

        self.status_var.set("Running")

    ##############################################
    # stop running audio
    ##############################################
    def stop_audio(self):
        self.running = False
        self.status_var.set("Stopped")


    ##############################################
    # update the plot
    ##############################################
    def _update_plot(self):
        with self.lock:
            t = self.last_plot_t
            pg = self.last_plot_pg
            pe = self.last_plot_pe
            omega = self.omega
            detuning = self.detuning

        if t is None:
            t = np.linspace(0, self.plot_duration, self.plot_points)
            pg, pe = self.probabilities(t, omega, detuning)

        self.line_pg.set_data(t, pg)
        self.line_pe.set_data(t, pe)
        self.ax.set_xlim(t[0], t[-1])
        self.ax.set_title(f"Spin probabilities vs time   |   Ω = {omega:.2f}, Δω = {detuning:.2f}")
        self.canvas.draw_idle()

        self.root.after(50, self._update_plot)

    ##############################################
    # when the window is closed
    ##############################################
    def on_close(self):
        self.running = False
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

# main method
if __name__ == "__main__":
    app = RabiSonifier()
    app.run()