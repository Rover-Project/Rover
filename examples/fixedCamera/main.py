import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import threading

from roverlib.plugins.camera.camera import Camera


class CameraGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Rover Camera Test")
        self.root.geometry("1000x700")

        self.camera = None
        self.running = False

        self.create_widgets()

    # UI
    def create_widgets(self):

        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Start / Stop
        ttk.Button(control_frame, text="Start Camera", command=self.start_camera).pack(pady=5)
        ttk.Button(control_frame, text="Stop Camera", command=self.stop_camera).pack(pady=5)

        # FPS
        ttk.Label(control_frame, text="FPS").pack()
        self.fps_var = tk.IntVar(value=30)
        ttk.Spinbox(control_frame, from_=1, to=120, textvariable=self.fps_var, command=self.update_fps).pack()

        # Format
        ttk.Label(control_frame, text="Format").pack()
        self.format_var = tk.StringVar(value="rgb")
        format_box = ttk.Combobox(control_frame, textvariable=self.format_var)
        format_box["values"] = ["rgb", "bgr", "gray", "hsv"]
        format_box.pack()
        format_box.bind("<<ComboboxSelected>>", lambda e: self.update_format())

        # Exposure
        ttk.Label(control_frame, text="Exposure (us)").pack()
        self.exposure_var = tk.IntVar(value=10000)
        ttk.Entry(control_frame, textvariable=self.exposure_var).pack()

        ttk.Label(control_frame, text="Gain").pack()
        self.gain_var = tk.DoubleVar(value=1.0)
        ttk.Entry(control_frame, textvariable=self.gain_var).pack()

        ttk.Button(control_frame, text="Manual Exposure", command=self.set_manual_exposure).pack(pady=5)
        ttk.Button(control_frame, text="Auto Exposure", command=self.enable_auto_exposure).pack(pady=5)

        # Capture
        ttk.Button(control_frame, text="Capture Image", command=self.capture_image).pack(pady=10)

        # Preview area
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(side=tk.RIGHT, expand=True)

    # Camera Controls 
    def start_camera(self):
        if self.camera is None:
            self.camera = Camera(
                width=640,
                height=480,
                fps=self.fps_var.get()
            )

        self.camera.start()
        self.running = True
        threading.Thread(target=self.update_frame, daemon=True).start()

    def stop_camera(self):
        if self.camera:
            self.camera.stop()
        self.running = False

    def update_fps(self):
        if self.camera:
            self.camera.set_FPS(self.fps_var.get())

    def update_format(self):
        if self.camera:
            self.camera.setFormat(self.format_var.get())

    def set_manual_exposure(self):
        if self.camera:
            self.camera.setExposure(
                self.exposure_var.get(),
                self.gain_var.get()
            )

    def enable_auto_exposure(self):
        if self.camera:
            self.camera.enableExposure()

    def capture_image(self):
        if self.camera and self.camera.isRunning():
            file = filedialog.asksaveasfilename(defaultextension=".jpg")
            if file:
                self.camera.getPicture(file)

   
    # Frame Update
    def update_frame(self):
        while self.running:
            frame = self.camera.getFrame()

            if len(frame.shape) == 2:  # gray
                frame = np.stack((frame,) * 3, axis=-1)

            img = Image.fromarray(frame)
            img = img.resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

    # Cleanup
    def on_close(self):
        self.running = False
        if self.camera:
            self.camera.cleanup()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
