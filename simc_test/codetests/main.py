import subprocess
from tqdm import tqdm
import os
import glob
import shutil


def get_simc_codes():
    remove_simc_repo()
    _ = subprocess.getoutput("git clone https://github.com/cimplec/sim-c")


def remove_simc_repo():
    if os.path.exists("sim-c"):
        try:
            shutil.rmtree("sim-c")
        except:
            _ = subprocess.getoutput('rd /s /q "sim-c"')


def run_simc_codes():
    get_simc_codes()
    os.chdir("sim-c/simc-codes")

    files = glob.glob("*.simc")

    correct = 0
    wrong = {}

    for i in tqdm(range(len(files))):
        filename_c = "".join(os.path.basename(files[i]).split(".")[:-1]) + ".c"
        output = subprocess.getoutput(f"simc {files[i]}")
        if "C code generated at" in output:
            correct += 1
        else:
            wrong[files[i]] = output

    print(f"\033[92m[{correct}/{len(files)}] tests passed!")
    print(f"\033[91m[{len(wrong)}/{len(files)}] tests failed!\n")
    if len(wrong) > 0:
        print(f"\033[1;37;0mThe list of files that failed to pass test are:-")
        for file, error_msg in wrong.items():
            print(f"\033[1;37;0m{file} - {error_msg}")

    os.chdir("../../")
    remove_simc_repo()
