import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar
import time
import queue
import threading


class Q2SplashGui:
    def __init__(self, q: queue.Queue, max=None):
        self.q = q
        self.max = max

        self.root = tk.Tk()
        self.root.withdraw()

        self.splash_screen = tk.Toplevel(background="gray")
        self.splash_screen.overrideredirect(True)
        self.splash_screen.title("Splash Screen")
        width, height, x, y = self.centerWindow()
        self.splash_screen.geometry(f"{width}x{height}+{x}+{y}")

        self.pb_frame = tk.Frame(self.splash_screen)
        self.pb_frame.pack()

        self.label = tk.Label(self.pb_frame, text="")
        self.label.pack(fill=tk.X, side=tk.RIGHT)

        self.progressbar = Progressbar(
            self.pb_frame,
            orient=tk.HORIZONTAL,
            length=width,
            mode="determinate" if self.max else "indeterminate",
            maximum=self.max if self.max else 50,
        )
        self.progressbar.pack(side=tk.LEFT)

        self.stdoutput = ScrolledText(self.splash_screen, padx=10, pady=10)
        self.stdoutput.config(state=tk.DISABLED)
        self.stdoutput.pack(fill=tk.BOTH, expand=True)

        self.root.after(1, self.auto_step)
        self.root.mainloop()

    def auto_step(self):
        self.step()
        task = self.q.get()
        if task is None:
            self.root.destroy()
        elif task == "__hide__":
            self.splash_screen.withdraw()
        elif task == "__show__":
            self.splash_screen.deiconify()
        else:
            self.set_text(task)
        self.root.after(10, self.auto_step)

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

    def centerWindow(self):  # Return 4 values needed to center Window
        screen_width = self.root.winfo_screenwidth()  # Width of the screen
        screen_height = self.root.winfo_screenheight()  # Height of the screen
        width = screen_width / 4
        height = screen_height / 3
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        return int(width), int(height), int(x), int(y)

    def update(self):
        self.root.update()

    def close(self):
        self.splash_screen.destroy()


class Q2Splash(threading.Thread):
    class RepeatTimer(threading.Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    def __init__(self):
        self.queue = queue.Queue()
        super().__init__()
        self.splash = None
        # self.timer = self.RepeatTimer(interval=0.05, function=self.tick)
        self.start()

    def put(self, data):
        self.queue.put(data)

    def tick(self):
        print(1)
        self.splash.step()

    def run(self):
        self.splash = Q2SplashGui(self.queue)

    def close(self):
        self.join()


if __name__ == "__main__":
    splash_window = Q2Splash()
    for x in range(10):
        splash_window.put(f"x {x} --")
        time.sleep(0.2)
    splash_window.put("__hide__")
    for x in range(10):
        splash_window.put(f"y {x} --")
        time.sleep(0.2)

    splash_window.put("__show__")
    for x in range(10):
        splash_window.put(f"z {x} --")
        time.sleep(0.2)
    time.sleep(5)
    splash_window.put(None)
    print("done")
