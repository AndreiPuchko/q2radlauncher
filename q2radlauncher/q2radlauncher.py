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

        if self.run_q2rad_executable():
            sys.exit(0)
        self.run()

        self.t = Q2Terminal(echo=True)

        if not self.check_python():
            sys.exit(1)
        if not self.check_folder():
            sys.exit(2)

        self.t.run(f"cd {self.q2rad_folder}")

        # run splash
        if not self.check_pip():
            sys.exit(3)
        if not self.check_virtualenv():
            sys.exit(4)

        if not self.activate_virtualenv():
            sys.exit(5)
        if not self.run_q2rad():
            self.install_q2rad()
            if not self.run_q2rad():
                sys.exit(6)

    def check_python(self):
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
        if not os.path.isdir(self.q2rad_folder):
            os.mkdir(self.q2rad_folder)

        if not os.path.isdir(self.q2rad_folder):
            mess("Can not create folder: q2rad")
            return False
        return True

    def check_pip(self):
        self.t.run(f"{self.python} -m pip --version")
        if self.t.exit_code != 0:
            mess("install pip")
            return False
        return True

    def check_virtualenv(self):
        self.t.run(f"{self.python} -m virtualenv --version")
        if self.t.exit_code != 0:
            self.t.run(f"{self.python} -m pip install --upgrade virtualenv")
        self.t.run(f"{self.python} -m virtualenv --version")
        if self.t.exit_code != 0:
            mess("Can not install virtualenv")
            return False
        return True

    def activate_virtualenv(self):
        if "win32" in sys.platform:
            self.t.run(f"{self.q2rad_folder}/scripts/activate")
        else:
            self.t.run(f"source {self.q2rad_folder}/bin/activate")

        if self.t.exit_code != 0:
            self.t.run("echo create virtualenv")
            self.t.run("pwd")
            self.t.run(f"{self.python} -m virtualenv q2rad")
        else:
            return True

        if "win32" in sys.platform:
            self.t.run(f"{self.q2rad_folder}/scripts/activate")
        else:
            self.t.run(f"source {self.q2rad_folder}/bin/activate")
        if self.t.exit_code != 0:
            return False
        return True

    def run_q2rad(self):
        self.t.run(f"{self.python} -m q2rad")
        if self.t.exit_code != 0:
            return False
        return True

    def install_q2rad(self):
        self.t.run(f"{self.python} -m pip install --upgrade q2rad")
        if self.t.exit_code != 0:
            return False
        return True

    def run_q2rad_executable(self):
        t = Q2Terminal(echo=True)
        t.run(f"cd {self.q2rad_folder}")
        if t.exit_code != 0:
            return False

        if "win32" in sys.platform:
            t.run(f"{self.q2rad_folder}/scripts/q2rad")
        else:
            t.run(f"source {self.q2rad_folder}/bin/q2rad")
        if t.exit_code != 0:
            return False
        return True

    def run(self):
        self.t = Q2Terminal(echo=True)
        self.t.run(f"cd {self.q2rad_folder}")
        if self.t.exit_code != 0:
            return False
        if self.activate_virtualenv():
            if self.run_q2rad():
                sys.exit(0)
        return False


launcher()
