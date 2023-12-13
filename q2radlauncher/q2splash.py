import sys
import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar

import time
import queue
import threading
import re
import logging

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
RED = "\x1b[38;5;1m"
GREEN = "\x1b[38;5;2m"
YELLOW = "\x1b[38;5;3m"
RESET = "\x1b[0;0m"
CLEAR = "\x1b[2J"


color_tags = {RED: "red", GREEN: "green", YELLOW: "brown"}


class Q2Worker(threading.Thread):
    def __init__(self, worker, splash):
        super().__init__()
        self.worker = worker
        self.splash = splash

    def run(self):
        self.worker(self.splash)


logo_png = (
    "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAAAAAAeW/F+AAAAIGNIUk0AAHomAACAhAAA+"
    "gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAAACYktHRAD/h4/MvwAAAAd0SU1FB+cFHg"
    "sGB3vY84IAAAEdSURBVCjPpdOxSgNBEAbgPwaDIVh4QTDaXLQR7h0CWlncO9iovSDmHYT"
    "4Aq4kDyBWuUZrD8ReJBZ6tqISk4OQcK7Fzc7m5owITjd8sPyzs1vQ+K3m8Fee3I/yrk0l"
    "7XprrEUxJ50qFk/HMzjpVIG8Y1rzjozmPOULh6NWziZ9y+lgtRXm5dX2bk8OFnrUul3lY"
    "Lsnk5O7XeUA1nnu0APgBudpCuP21kIP9UCZjOSW9c1OoJY409ajTQ4AWFuvPQ+4e/nIri"
    "Ty0bg7mifduM4eHvmAdVLmyAesGzVMSs5K/ORzpMbt4eaVWIlaYC6e9B++BA+bJaN7bz8"
    "8h5hcKCdPXaqdO26WUNwXOnXn8XH54F3PZP15+SpVF/71x74B2VDrDoJd9WMAAAAldEVY"
    "dGRhdGU6Y3JlYXRlADIwMjMtMDUtMzBUMTE6MDY6MDcrMDA6MDDQ1Gu2AAAAJXRFWHRkY"
    "XRlOm1vZGlmeQAyMDIzLTA1LTMwVDExOjA2OjA3KzAwOjAwoYnTCgAAACh0RVh0ZGF0ZT"
    "p0aW1lc3RhbXAAMjAyMy0wNS0zMFQxMTowNjowNyswMDowMPac8tUAAAAASUVORK5CYII="
)


class Q2Splash:
    def __init__(self, queue=queue.Queue(), max=None, width=None, height=None, worker=None):
        if worker is None:
            return
        self.queue = queue
        self.max = max

        self.root = tk.Tk()
        self.root.withdraw()

        self.after_interval = 10
        self.splash_screen = tk.Toplevel()
        # self.splash_screen.overrideredirect(True)

        self.splash_screen.protocol("WM_DELETE_WINDOW", self.close_windows_event)
        self.splash_screen.resizable(0, 0)

        self.splash_screen.transient()
        self.splash_screen.title("q2rad launcher")
        self.centerWindow(width, height)

        self.create_gui()
        self.worker = Q2Worker(worker, self)
        self.timeout = 0
        self.timestart = time.time()
        self.is_error = False
        self.current_color = None
        self.worker_started = False
        # self.start_worker()
        self.splash_screen.mainloop()

    def start_worker(self):
        self.worker_started = True
        self.worker.start()
        # self.pb_frame.grid()
        self.show_progressbar()
        self.options_frame.grid_remove()
        self.show_progressbar()

    def close_windows_event(self):
        if not self.worker_started:
            self.exit()

    def create_gui(self):
        if 0.1:  # title frame
            self.title_frame = tk.Frame(self.splash_screen)
            im = tk.PhotoImage(data=logo_png)
            self.icon = tk.Label(self.title_frame, image=im, text="")
            self.icon.image = im
            self.icon.pack(side="left")

            self.title = tk.Label(self.title_frame, text="q2rad online installer", font=("", 20))
            self.title.pack(anchor=tk.S, side="left", fill=tk.BOTH)
            self.title_frame.grid(row=0, column=0, sticky=tk.W)

        if 1:  # options frame
            self.radio_value = tk.IntVar()
            self.radio_value.set(1)

            self.options_frame = tk.Frame(self.splash_screen)
            self.radio_local = tk.Radiobutton(
                self.options_frame, text="Local python folder", variable=self.radio_value, value=1
            )
            self.radio_venv = tk.Radiobutton(
                self.options_frame, text="Global python with Venv", variable=self.radio_value, value=2
            )

            self.install_button = tk.Button(self.options_frame, text="Install", command=self.start_worker)
            self.close_button = tk.Button(self.options_frame, text="Close", command=self.close_windows_event)
            self.radio_local.pack(side=tk.LEFT)
            self.radio_venv.pack(side=tk.LEFT)
            self.install_button.pack(side=tk.LEFT, padx=20, pady=5, ipadx=10)
            self.close_button.pack(side=tk.LEFT, padx=20, pady=5, ipadx=10)
            self.options_frame.grid(row=1, column=0)

        if 2:  # progressbar text
            self.pb_frame = tk.Frame(self.splash_screen)
            self.progress_stage = tk.Label(self.pb_frame, text="Task", font=("", 14))
            self.progress_stage.pack(side=tk.TOP, fill="x", expand="no")

            self.progress_label = tk.Label(self.pb_frame, text="6555")
            self.progress_label.pack(fill=tk.X, side=tk.RIGHT)

            self.progressbar = Progressbar(
                self.pb_frame,
                orient=tk.HORIZONTAL,
                length=self.splash_screen.winfo_screenwidth(),
                mode="determinate" if self.max else "indeterminate",
                maximum=self.max if self.max else 50,
            )
            self.progressbar.pack(side=tk.LEFT)
            self.pb_frame.grid(row=2, column=0)
            self.hide_progressbar()
            # self.pb_frame.grid_remove()

        if 3:
            self.stdoutput = ScrolledText(self.splash_screen)
            self.stdoutput.config(state=tk.DISABLED)
            self.stdoutput.tag_config("red", foreground="red")
            self.stdoutput.tag_config("red", foreground="red")
            self.stdoutput.tag_config("green", foreground="green")
            self.stdoutput.tag_config("yellow", foreground="yellow")
            self.stdoutput.grid_propagate(False)
            self.stdoutput.grid(row=3, column=0)

        if 4:
            self.error_button_frame = tk.Frame(self.splash_screen)
            self.error_button = tk.Button(
                self.error_button_frame, text="Close", command=self.done_button_click
            )
            self.error_button.pack(padx=5, pady=5)
            self.error_button_frame.grid(row=4, column=0)
            self.error_button_frame.grid_remove()

        if 4:
            self.done_button_frame = tk.Frame(self.splash_screen)
            self.done_button = tk.Button(
                self.done_button_frame, text="Close", command=self.done_button_click
            )
            self.done_button.pack(padx=5, pady=5)
            self.done_button_frame.grid(row=4, column=0)
            self.done_button_frame.grid_remove()

        self.splash_screen.grid_rowconfigure(0, weight=1)
        self.splash_screen.grid_rowconfigure(1, weight=1)
        self.splash_screen.grid_rowconfigure(2, weight=1)
        self.splash_screen.grid_rowconfigure(3, weight=5)
        self.splash_screen.grid_rowconfigure(4, weight=1)

        self.splash_screen.grid_columnconfigure(0, weight=1)

        self.splash_screen.after(self.after_interval, self.auto_step)
        self.starttime = time.time()

    def hide_progressbar(self):
        print("hide pb")
        self.pb_frame.grid_remove()


    def show_progressbar(self):
        # self.progress_stage.pack(anchor=tk.W, side="top")
        # self.progress_stage.grid()
        self.pb_frame.grid()

    def show_done_button(self):
        self.hide_progressbar()
        self.done_button_frame.grid()
        self.root.update()

    def auto_step(self):
        if os.path.isfile("./q2rad/log/q2.log"):
            if os.path.getmtime("./q2rad/log/q2.log") > self.timestart:
                self.exit()
        if self.timeout:
            if time.time() - self.timeout_startpoint > self.timeout:
                self.exit()

        self.step()
        if self.queue.qsize() > 0:
            task = self.queue.get()
            if task is None:
                self.exit()
            elif task == "":
                pass
            elif task == "__hide__" or "Starting q2rad..." in task or "Successfully installed" in task:
                self.splash_screen.withdraw()
            elif task == "__show__":
                self.splash_screen.deiconify()
            elif task == "__error__":
                self.show_done_button()
            else:
                self.set_text(task)
            self.root.update()
        self.splash_screen.after(self.after_interval, self.auto_step)

    def done_button_click(self):
        self.is_error = False
        self.exit()

    def exit(self):
        if self.is_error:
            pass
        else:
            self.hide()
            self.root.update()
            self.set_timeout()
            self.splash_screen.destroy()
            self.root.destroy()
            sys.exit(0)

    def step(self):
        self.progressbar.step()
        pb_value = int(self.progressbar["value"])
        if self.max is None:
            tm = round((time.time() - self.starttime), 2)
            self.progress_label.config(text=f"{tm:0.2f}")
        else:
            self.progress_label.config(text=f"{pb_value}%")
        self.root.update()

    def set_text(self, text):
        if ansi_escape.match(text):
            self.current_color = color_tags.get(ansi_escape.match(text)[0])
        else:
            self.current_color = ""
        text = ansi_escape.sub("", text)

        if chr(13) in text:
            text = text.split(chr(13))[-1]

        if self.current_color:
            self.progress_stage.config(text=text)

        if text.strip() == "":
            return
        logging.debug(text)

        self.stdoutput.config(state=tk.NORMAL)
        self.stdoutput.insert(tk.END, f"{text}\n", self.current_color)
        self.stdoutput.see(tk.END)
        self.stdoutput.config(state=tk.DISABLED)

    def centerWindow(self, width=None, height=None):
        screen_width = self.root.winfo_screenwidth()  # Width of the screen
        screen_height = self.root.winfo_screenheight()  # Height of the screen
        if width is None:
            width = screen_width // 4
        if height is None:
            height = screen_height // 3
        width = self.prep_size(width, screen_width)
        height = self.prep_size(height, screen_height)
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.splash_screen.geometry(f"{width}x{height}+{x}+{y}")

    def prep_size(self, width, screen_width):
        if isinstance(width, str):
            if width.endswith("%"):
                width = int(screen_width / 100 * int(width[:-1]))
            else:
                width = int(width)
        return width

    def put(self, data):
        self.queue.put(data)

    def update(self):
        self.root.update()

    def close(self):
        self.put(None)

    def set_timeout(self, timeout=0):
        self.timeout = timeout
        self.timeout_startpoint = time.time()

    def hide(self):
        self.queue.put("__hide__")

    def show(self):
        self.queue.put("__show__")


if __name__ == "__main__":
    # Demo
    def worker(splash: Q2Splash):
        splash.put(RED + " 111 " + RESET)
        t = time.time()
        elapsed = lambda: time.time() - t
        while elapsed() < 6:
            splash.put(f"time {elapsed()} --")
            time.sleep(0.4)
        splash.show_done_button()
        # splash.close()
        print("done")

    Q2Splash(worker=worker)
