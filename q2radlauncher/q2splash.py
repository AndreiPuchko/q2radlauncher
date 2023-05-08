import tkinter as tk
from tkinter.scrolledtext import ScrolledText as sText
from tkinter.ttk import Progressbar
import time
import queue
import threading

q = queue.Queue()

class Q2Splash:
    def __init__(self, q: queue.Queue, max=None):
        self.q = q
        self.max = max

        self.root = tk.Tk()
        self.root.withdraw()

        self.splash_screen = tk.Toplevel(background="gray")
        # self.splash_screen.withdraw()
        self.splash_screen.overrideredirect(True)
        self.splash_screen.title("Splash Screen")
        width, height, x, y = self.centerWindow()
        self.splash_screen.geometry(f"{width}x{height}+{x}+{y}")

        self.label = tk.Label(self.splash_screen, text="")
        self.label.pack(fill=tk.X, side=tk.TOP)

        self.pb = Progressbar(
            self.splash_screen,
            orient=tk.HORIZONTAL,
            length=width,
            mode="determinate" if self.max else "indeterminate",
            maximum=self.max if self.max else 50,
        )
        self.pb.pack()

        self.text = sText(self.splash_screen, padx=10, pady=10)
        self.text.config(state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.root.after(10, self.auto_step)
        self.root.update()
        # if (self.q.qsize()) > 0:
        #     self.splash_screen.deiconify()

    def auto_step(self):
        task = self.q.get()
        if task is None:
            self.root.destroy()
        else:
            self.step()
            self.set_text(task)
        self.root.after(1, self.auto_step)

    def step(self):
        self.pb.step()
        pb_value = int(self.pb["value"])
        if self.max is None:
            self.label.config(text=f"{pb_value}")
        else:
            self.label.config(text=f"{pb_value}%")
        self.root.update()

    def set_text(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"{text}\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

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


class Worker(threading.Thread):
    def __init__(self, q):
        self.q = q
        super().__init__()

    def run(self):
        for x in range(100):
            self.q.put(f"{x} --")
            time.sleep(0.0001)
        self.q.put(None)


if __name__ == "__main__":
    w = Worker(q)
    w.start()
    sw = Q2Splash(q)
    sw.root.mainloop()

    print("done")
