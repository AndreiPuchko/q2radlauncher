import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar
import time
import queue
import threading


class Q2SplashGui:
    def __init__(self, q: queue.Queue, max=None, width=None, height=None):
        self.q = q
        self.max = max

        self.root = tk.Tk()
        self.root.withdraw()

        self.after_interval = 10
        self.splash_screen = tk.Toplevel()
        self.splash_screen.overrideredirect(True)
        self.splash_screen.title("Splash Screen")
        width, height, x, y = self.centerWindow(width, height)
        self.splash_screen.geometry(f"{width}x{height}+{x}+{y}")

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
        self.stdoutput.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.splash_screen.after(self.after_interval, self.auto_step)

    def auto_step(self):
        self.step()
        task = self.q.get()
        if task is None:
            self.root.destroy()
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
            self.label.config(text=f"{pb_value}")
        else:
            self.label.config(text=f"{pb_value}%")
        self.root.update()

    def set_text(self, text):
        self.stdoutput.config(state=tk.NORMAL)
        self.stdoutput.insert(tk.END, f"{text}\n")
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
                width=int(width)
        return width

    def update(self):
        self.root.update()

    def close(self):
        self.splash_screen.destroy()


class Q2Splash(threading.Thread):
    class RepeatTimer(threading.Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    def __init__(self, width=None, height=None):
        super().__init__()
        self.queue = queue.Queue()
        print(width)
        self.width = width
        self.height = height
        self.splash = None
        self.timer = self.RepeatTimer(interval=0.05, function=self.timer_tick)
        self.timer.start()
        self.start()

    def put(self, data):
        self.queue.put(data)
        if data is None:
            self.timer.cancel()

    def timer_tick(self):
        if self.queue.qsize() == 0:
            self.put("")
        if self.splash:
            self.splash.auto_step()

    def run(self):
        print(self.width)
        self.splash = Q2SplashGui(self.queue, width=self.width, height=self.height)

    def close(self):
        self.put(None)


if __name__ == "__main__":
    # Demo
    splash_window = Q2Splash(width="50%", height="50%")
    for x in range(10):
        splash_window.put(f"x {x} --")
        # time.sleep(0.2)

    splash_window.put("__hide__")
    for x in range(10):
        splash_window.put(f"y {x} --")
        # time.sleep(0.2)

    splash_window.put("__show__")
    for x in range(10):
        splash_window.put(f"z {x} --")
        # time.sleep(0.2)
    time.sleep(2)
    splash_window.close()
    print("done")
