from q2terminal.q2terminal import Q2Terminal
import sys
import os
from packaging import version
from tkinter import messagebox
from q2splash import Q2Splash, GREEN, RED
import urllib.request
import logging


if "darwin" in sys.platform:
    path = sys.argv[0].split("/Contents/MacOS")[0]
    path = os.path.dirname(path)
    os.chdir(path)


messagebox_title = "q2rad launcher"


def mess(text):
    messagebox.showerror(
        messagebox_title,
        text,
    )


logging.basicConfig(
    filename="q2launcher.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s] - %(message)s",
)


class launcher:
    def __init__(self, splash: Q2Splash = None):
        if "win32" in sys.platform:
            self.python = "py"
        else:
            self.python = "python3"

        self.q2rad_folder = "./q2rad"
        self.splash = splash
        self.remove_temp_file()

        self.put(GREEN + "Starting q2rad...")
        if self.run_q2rad_executable():
            self.exit(0)
        if self.run_q2rad_python():
            self.exit(0)
        self.splash.centerWindow("70%", "50%")
        self.put(RED + "q2rad did not start...")

        self.t = Q2Terminal(callback=self.terminal_callback)
        self.put(GREEN + "Downloading get-q2rad.py...")
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/AndreiPuchko/q2rad/main/install/get-q2rad.py",
            "_tmp.py",
        )

        self.t.run(f"{self.python} _tmp.py")
        self.remove_temp_file()

        self.exit()

    def remove_temp_file(self):
        if os.path.isfile("_tmp.py"):
            os.remove("_tmp.py")

    def put(self, text):
        if self.splash:
            self.splash.put(text)
        else:
            print(text)

    def exit(self, exit_code=0):
        self.put(None)
        sys.exit(exit_code)

    def hide(self):
        self.put("__hide__")

    def show_splash(self):
        self.put("__show__")

    def terminal_callback(self, text):
        if text in ["True", "False", "0", "1"]:
            return
        self.put(text)

    def check_python(self):
        self.put("Checking python version...")
        python_version = (
            self.t.run(f"{self.python} --version")[0].lower().replace("python ", "")
        )

        if self.t.exit_code != 0:
            self.splash.hide()
            mess("Python was not found, go to www.python.org")
            return False

        if version.parse(python_version) < version.parse("3.8.1"):
            self.splash.hide()
            mess("Python version must be at least 3.8.1")
            return False
        return True

    def check_folder(self):
        self.put("Checking folder...")
        if not os.path.isdir(self.q2rad_folder):
            os.mkdir(self.q2rad_folder)

        if not os.path.isdir(self.q2rad_folder):
            self.splash.hide()
            mess("Can not create folder: q2rad")
            return False
        return True

    def activate_virtualenv(self):
        try_to_create = True
        while True:
            if self.splash:
                self.put("Activating virtualenv...")
            if "win32" in sys.platform:
                self.t.run(f"{self.q2rad_folder}/scripts/activate")
            else:
                self.t.run(f"source {self.q2rad_folder}/bin/activate")
            if self.t.exit_code != 0 and try_to_create:
                if self.create_virtualenv():
                    try_to_create = False
                    continue
                else:
                    return False
            else:
                break
        return True

    def create_virtualenv(self):
        self.put("Creating virtualenv...")
        self.t.run(f"{self.python} -m virtualenv q2rad")
        if self.t.exit_code != 0:
            return False
        return True

    def install_q2rad(self):
        self.show_splash()
        self.put("Installing q2rad...")
        self.t.run(f"{self.python} -m pip install --upgrade q2rad")
        if self.t.exit_code != 0:
            return False
        return True

    def run_q2rad(self):
        # self.hide_splash()
        self.set_timeout(10)
        self.t.run(f"{self.python} -m q2rad")
        self.set_timeout(0)
        if self.t.exit_code != 0:
            return False
        return True

    def run_q2rad_executable(self):
        self.put("Starting q2rad executable...")
        t = Q2Terminal()
        t.run(f"cd {self.q2rad_folder}")

        if t.exit_code != 0:
            return False

        self.set_timeout(10)

        if "win32" in sys.platform:
            t.run(f"{self.q2rad_folder}/scripts/q2rad")
        else:
            t.run(f"./{self.q2rad_folder}/bin/q2rad")
        if t.exit_code != 0:
            self.set_timeout(0)
            return False
        return True

    def run_q2rad_python(self):
        self.put("Starting q2rad package...")
        self.t = Q2Terminal()
        self.t.run(f"cd {self.q2rad_folder}")
        if self.t.exit_code != 0:
            return False
        if self.activate_virtualenv():
            if self.run_q2rad():
                self.exit(0)
        return False

    def set_timeout(self, timeout=0):
        if self.splash:
            self.splash.set_timeout(timeout)


def worker(splash):
    launcher(splash)


Q2Splash(worker=worker, width="15%", height="15%")
