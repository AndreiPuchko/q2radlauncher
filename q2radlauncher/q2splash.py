from collections.abc import Callable, Iterable, Mapping
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

logging.basicConfig(
    filename="q2launcher.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
)

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


class Q2Splash:
    def __init__(
        self, queue=queue.Queue(), max=None, width=None, height=None, worker=None
    ):
        if worker is None:
            return
        self.queue = queue
        self.max = max

        self.root = tk.Tk()
        self.root.withdraw()

        self.after_interval = 10
        self.splash_screen = tk.Toplevel()
        self.splash_screen.overrideredirect(True)
        self.splash_screen.title("q2rad launcher")
        # self.splash_screen.iconbitmap("q2rad.ico")
        width, height, x, y = self.centerWindow(width, height)
        self.splash_screen.geometry(f"{width}x{height}+{x}+{y}")

        self.worker = Q2Worker(worker, self)
        self.worker.start()
        self.timeout = 0
        self.timestart = time.time()
        self.create_gui()
        self.splash_screen.mainloop()

    def create_gui(self):
        self.pb_frame = tk.Frame(self.splash_screen)
        self.pb_frame.pack()

        self.label = tk.Label(self.pb_frame, text="")
        self.label.pack(fill=tk.X, side=tk.RIGHT)

        self.progressbar = Progressbar(
            self.pb_frame,
            orient=tk.HORIZONTAL,
            length=self.splash_screen.winfo_screenwidth(),
            mode="determinate" if self.max else "indeterminate",
            maximum=self.max if self.max else 50,
        )
        self.progressbar.pack(side=tk.LEFT, expand=True, padx=5, pady=5)

        self.stdoutput = ScrolledText(self.splash_screen)
        self.stdoutput.config(state=tk.DISABLED)
        self.stdoutput.tag_config("red", foreground="red")
        self.stdoutput.tag_config("red", foreground="red")
        self.stdoutput.tag_config("green", foreground="green")
        self.stdoutput.tag_config("yellow", foreground="yellow")
        self.current_color = None
        self.stdoutput.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.splash_screen.after(self.after_interval, self.auto_step)

    def auto_step(self):
        if os.path.isfile("./q2rad/log/q2.log"):
            if os.path.getmtime("./q2rad/log/q2.log") > self.timestart:
                self.put(None)

        if self.timeout:
            if time.time() - self.timeout_startpoint > self.timeout:
                self.hide()
                self.set_timeout()
                self.root.destroy()
                sys.exit(0)

        self.step()
        if self.queue.qsize() > 0:
            task = self.queue.get()
            if task is None:
                self.root.destroy()
                sys.exit(0)
            elif task == "":
                pass
            elif task == "__hide__":
                self.splash_screen.withdraw()
            elif task == "__show__":
                self.splash_screen.deiconify()
            else:
                self.set_text(task)
        self.splash_screen.after(self.after_interval, self.auto_step)

    def step(self):
        self.progressbar.step()
        pb_value = int(self.progressbar["value"])
        if self.max is None:
            self.label.config(text=f"{pb_value/10}")
        else:
            self.label.config(text=f"{pb_value}%")
        self.root.update()

    def set_text(self, text):
        # color = self.current_color
        if ansi_escape.match(text):
            self.current_color = color_tags.get(ansi_escape.match(text)[0])
        else:
            self.current_color = ""
        text = ansi_escape.sub("", text)

        if chr(13) in text:
            text = text.split(chr(13))[-1]

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
            width = screen_width / 4
        if height is None:
            height = screen_height / 3
        width = self.prep_size(width, screen_width)
        height = self.prep_size(height, screen_height)
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        return int(width), int(height), int(x), int(y)

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
    def worker(splash):
        # splash_window = Q2Splash(width="50%", height="50%")
        splash.set_timeout(5)
        splash.put("111")
        for x in range(10):
            splash.put(f"x {x} --")
            time.sleep(1)
        splash.set_timeout()

        splash.hide()
        for x in range(10):
            splash.put(f"y {x} --")
            time.sleep(0.2)
        splash.show()

        for x in range(10):
            splash.put(f"z {x} --")
            time.sleep(0.2)
        time.sleep(2)
        splash.close()
        print("done")

    Q2Splash(worker=worker, width="60%")
