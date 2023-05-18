import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar
import time
import queue
import threading


class Q2Worker(threading.Thread):
    def __init__(self, worker, splash):
        super().__init__()
        self.worker = worker
        self.splash = splash

    def run(self):
        self.worker(self.splash)


class Q2Splash:
    def __init__(
        self,
        q: queue.Queue = queue.Queue(),
        max=None,
        width=None,
        height=None,
        worker=None,
    ):
        if worker is None:
            return
        self.q = q
        self.max = max
        self.timeout = 0
        self.timeout_startpoint = 0

        self.root = tk.Tk()
        self.root.withdraw()

        self.after_interval = 100
        self.splash_screen = tk.Toplevel()
        self.splash_screen.overrideredirect(True)
        self.splash_screen.title("Splash Screen")
        width, height, x, y = self.centerWindow(width, height)
        self.splash_screen.geometry(f"{width}x{height}+{x}+{y}")

        # print(threading.Timer(1, lambda: worker(self)).start())
        self.worker = Q2Worker(worker, self)
        self.worker.start()
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
        if self.timeout:
            if time.time() - self.timeout_startpoint > self.timeout:
                self.hide()
                self.set_timeout(0)
        self.step()
        if self.q.qsize() > 0:
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
                width = int(width)
        return width

    def set_timeout(self, timeout):
        self.timeout = timeout
        self.timeout_startpoint = time.time()

    def put(self, data):
        self.q.put(data)

    def update(self):
        self.root.update()

    def close(self):
        self.put(None)

    def hide(self):
        self.put("__hide__")

    def show(self):
        self.put("__show__")


if __name__ == "__main__":

    def worker(splash_window: Q2Splash):
        splash_window.set_timeout(5)
        for x in range(10):
            splash_window.put(f"x {x} --")
            time.sleep(1)
        # splash_window.put(None)
        splash_window.hide()
        for x in range(10):
            splash_window.put(f"y {x} --")
            # time.sleep(0.2)

        splash_window.show()
        for x in range(10):
            splash_window.put(f"z {x} --")
            # time.sleep(0.2)
        time.sleep(2)
        splash_window.close()
        print("done")

    # Demo
    splash_window = Q2Splash(width="50%", height="50%", worker=worker)
