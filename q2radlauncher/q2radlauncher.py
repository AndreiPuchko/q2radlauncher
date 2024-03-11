from q2terminal.q2terminal import Q2Terminal
import sys
import os
from packaging import version
from tkinter import messagebox
from q2splash import Q2Splash, GREEN
import subprocess
import urllib.request
import zipfile
import logging
import time
import webbrowser

PYTHON_VERSION = "3.11.7"
PYTHON_FOLDER = f"q2rad/python.loc.{PYTHON_VERSION}"
PYTHON_SOURCE = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"


if "darwin" in sys.platform:
    path = sys.argv[0].split("/Contents/MacOS")[0]
    path = os.path.dirname(path)
    os.chdir(path)

start_dir = os.path.abspath(".")

messagebox_title = "q2rad launcher"


def mess(text):
    messagebox.showerror(
        messagebox_title,
        text,
    )


def run_q2rad():
    code_string = "from q2rad.q2rad import main;main()"
    bin_extention = "w.exe" if "win32" in sys.platform else ""

    if os.path.isfile(f"{PYTHON_FOLDER}/python{bin_extention}"):
        py3bin = os.path.abspath(f"{PYTHON_FOLDER}/python")
    elif os.path.isdir("q2rad/q2rad"):
        py3bin = os.path.abspath(
            f'q2rad/q2rad/{"Scripts" if "win32" in sys.platform else "bin"}/python{bin_extention}'
        )
    else:
        return False
    try:
        os.chdir("q2rad")
        if "win32" not in sys.platform:
            os.execv(py3bin, [py3bin, "-c", code_string])
        else:
            subprocess.Popen(
                ["powershell", f'&"{py3bin}"', "-c", f'"{code_string}"'],
                start_new_session=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        return True
    except Exception as e:
        print(e)
        os.chdir(start_dir)
    return False


if not os.path.isdir("q2rad"):
    os.makedirs("q2rad")


logging.basicConfig(
    filename="q2rad/q2launcher.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s] - %(message)s",
)


class launcher:
    def __init__(self, splash: Q2Splash = None):
        self.splash = splash
        self.terminal = Q2Terminal(callback=self.terminal_callback)
        if self.splash.radio_install_option.get() == self.splash.GLOBAL_PYTHON:
            self.install_global()
        else:
            self.install_local()

    def install_local(self):
        if not os.path.isdir(PYTHON_FOLDER):
            os.makedirs(PYTHON_FOLDER)

        self.terminal.run(f"cd {PYTHON_FOLDER}")

        if not os.path.isfile(f"{PYTHON_FOLDER}/python.exe"):
            if not os.path.isfile(f"{PYTHON_FOLDER}/python.zip"):
                self.put(GREEN + f"Downloading {PYTHON_SOURCE}...")
                urllib.request.urlretrieve(PYTHON_SOURCE, f"{PYTHON_FOLDER}/python.zip")
                self.put(GREEN + f"{PYTHON_SOURCE} downloaded.")

            with zipfile.ZipFile(f"{PYTHON_FOLDER}/python.zip", "r") as zip_ref:
                zip_ref.extractall(PYTHON_FOLDER)
                self.put(GREEN + f"{PYTHON_FOLDER}/python.zip unzipped.")
            os.remove(f"{PYTHON_FOLDER}/python.zip")

        self.prepare_pth()

        self.terminal.run("./python -m pip -V")
        if self.terminal.exit_code != 0:
            if not os.path.isfile(f"{PYTHON_FOLDER}/get-pip.py"):
                self.put(GREEN + "Downloading pip...")
                urllib.request.urlretrieve(
                    "https://bootstrap.pypa.io/get-pip.py", f"{PYTHON_FOLDER}/get-pip.py"
                )
                self.put(GREEN + "Pip downloaded.")
            self.put(GREEN + "Installing pip...")
            self.terminal.run("./python get-pip.py --no-warn-script-location")
            self.put(GREEN + "Pip installed.")
            if self.terminal.exit_code != 0:
                self.put(GREEN + "get-pip.py error!")
                return
            os.remove(f"{PYTHON_FOLDER}/get-pip.py")

        self.terminal.run("cd ../..")
        self.put(GREEN + "Install q2rad")
        self.terminal.run(f"{PYTHON_FOLDER}'/python' -m pip install --no-warn-script-location q2rad")
        self.put(GREEN + "q2rad installed.")
        self.splash.close()
        run_q2rad()

    def prepare_pth(self):
        vrs = "".join(PYTHON_VERSION.split(".")[:2])
        data = open(f"{PYTHON_FOLDER}/python{vrs}._pth").read()
        update = False
        if "#import site" in data:
            data = data.replace("#import site", "import site")
            update = True
        data0 = data.split("\n")
        if "Lib" not in data:
            data0.insert(1, "Lib")
            update = True
        if "Scripts" not in data:
            data0.insert(2, "Scripts")
            update = True
        if update:
            open(f"{PYTHON_FOLDER}/python{vrs}._pth", "w").write("\n".join(data0))

    def install_global(self):
        if "win32" in sys.platform:
            self.python = "py"
        else:
            self.python = "python3"

        self.q2rad_folder = "./q2rad"
        self.bin_folder = "Scripts" if "win32" in sys.platform else "bin"

        self.remove_temp_file()

        # self.put(GREEN + "Starting q2rad." + RESET)
        # if run_q2rad():
        #     self.exit()

        # self.splash.centerWindow("70%", "50%")
        # self.put(RED + "q2rad did not start...")

        self.put(GREEN + "Checking python...")
        time.sleep(0.5)
        if self.check_python() is False:
            self.splash.close()
            sys.exit()

        self.put(GREEN + "Installing q2rad...")
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/AndreiPuchko/q2rad/main/install/get-q2rad.py",
            "_tmp.py",
        )

        self.terminal.run(f"{self.python} _tmp.py")
        self.put(GREEN + "Done...")
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
        if "Failed to" in text or "FullyQualifiedErrorId" in text:
            self.put("__error__")

    def check_python(self):
        self.put(GREEN + "Checking python version...")
        python_version = self.terminal.run(f"{self.python} --version")[0].lower().replace("python ", "")

        if self.terminal.exit_code != 0:
            self.splash.hide()
            mess("Python was not found, please install and try again.")
            webbrowser.open("python.org/downloads")
            return False

        if version.parse(python_version) < version.parse("3.8.1"):
            self.splash.hide()
            mess("Python version must be at least 3.8.1")
            webbrowser.open("python.org/downloads")
            return False
        return True

    def set_timeout(self, timeout=0):
        if self.splash:
            self.splash.set_timeout(timeout)


def worker(splash):
    launcher(splash)


if run_q2rad():
    sys.exit(0)
else:
    Q2Splash(worker=worker)
