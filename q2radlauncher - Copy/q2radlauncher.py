from q2terminal.q2terminal import Q2Terminal
import sys
import os
from packaging import version
from tkinter import messagebox

from q2splash import Q2Splash


messagebox_title = "q2rad launcher"


def mess(text):
    messagebox.showerror(
        messagebox_title,
        text,
    )


class launcher:
    def __init__(self):
        if "win32" in sys.platform:
            self.python = "py"
        else:
            self.python = "python3"
        self.q2rad_folder = "q2rad"
        self.splash_window = None

        self.splash_window = Q2Splash(width="50%", height="50%")

        if self.run_q2rad_executable():
            self.exit(0)
        if self.run_q2rad_python():
            self.exit(0)
        self.splash_window.put("q2rad did not start...")

        self.t = Q2Terminal(callback=self.terminal_callback)

        if not self.check_python():
            self.exit(1)
        if not self.check_folder():
            self.exit(2)

        self.t.run(f"cd {self.q2rad_folder}")

        # run splash
        if not self.check_pip():
            self.exit(3)
        if not self.check_virtualenv():
            self.exit(4)
        if not self.activate_virtualenv():
            self.exit(5)
        if not self.run_q2rad():
            self.install_q2rad()
            if not self.run_q2rad():
                self.exit(6)
        self.splash_window.put(None)

    def exit(self, exit_code):
        if self.splash_window:
            self.splash_window.put(None)
        sys.exit(exit_code)

    def hide_splash(self):
        if self.splash_window:
            self.splash_window.put("__hide__")

    def show_splash(self):
        if self.splash_window:
            self.splash_window.put("__show__")

    def terminal_callback(self, text):
        if text in ["True", "False"]:
            return
        self.splash_window.put(text)

    def check_python(self):
        self.splash_window.put("Checking python version...")
        python_version = (
            self.t.run(f"{self.python} --version")[0].lower().replace("python ", "")
        )

        if self.t.exit_code != 0:
            mess("Python was not found, go to www.python.org")
            return False

        if version.parse(python_version) < version.parse("3.8.1"):
            mess("Python version must be at least 3.8.1")
            return False
        return True

    def check_folder(self):
        self.splash_window.put("Checking folder...")
        if not os.path.isdir(self.q2rad_folder):
            os.mkdir(self.q2rad_folder)

        if not os.path.isdir(self.q2rad_folder):
            mess("Can not create folder: q2rad")
            return False
        return True

    def check_pip(self):
        self.splash_window.put("Checking pip")
        self.t.run(f"{self.python} -m pip --version")
        if self.t.exit_code != 0:
            mess("install pip")
            return False
        return True

    def check_virtualenv(self):
        self.splash_window.put("Checking virtualenv...")
        self.t.run(f"{self.python} -m virtualenv --version")
        if self.t.exit_code != 0:
            self.splash_window.put("Installing virtualenv...")
            self.t.run(f"{self.python} -m pip install --upgrade virtualenv")
            # self.t.run(f"{self.python} -m virtualenv --version")
            if self.t.exit_code != 0:
                mess("Can not install virtualenv")
                return False
        return True

    def activate_virtualenv(self):
        try_to_create = True
        while True:
            if self.splash_window:
                self.splash_window.put("Activating virtualenv...")
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
        self.splash_window.put("Creating virtualenv...")
        self.t.run(f"{self.python} -m virtualenv q2rad")
        if self.t.exit_code != 0:
            return False
        return True

    def install_q2rad(self):
        self.show_splash()
        self.splash_window.put("Installing q2rad...")
        self.t.run(f"{self.python} -m pip install --upgrade q2rad")
        if self.t.exit_code != 0:
            return False
        return True

    def run_q2rad(self):
        # self.hide_splash()
        self.splash_window.set_timeout(10)
        self.t.run(f"{self.python} -m q2rad")
        self.splash_window.set_timeout(0)
        if self.t.exit_code != 0:
            return False
        return True

    def run_q2rad_executable(self):
        self.splash_window.put("Starting q2rad executable...")
        t = Q2Terminal()
        t.run(f"cd {self.q2rad_folder}")

        if t.exit_code != 0:
            return False

        self.splash_window.set_timeout(10)

        if "win32" in sys.platform:
            t.run(f"{self.q2rad_folder}/scripts/q2rad")
        else:
            t.run(f"source {self.q2rad_folder}/bin/q2rad")
        if t.exit_code != 0:
            self.splash_window.set_timeout(0)
            return False
        return True

    def run_q2rad_python(self):
        self.splash_window.put("Starting q2rad package...")
        self.t = Q2Terminal()
        self.t.run(f"cd {self.q2rad_folder}")
        if self.t.exit_code != 0:
            return False
        if self.activate_virtualenv():
            if self.run_q2rad():
                self.exit(0)
        return False


launcher()
