import subprocess
from tqdm import tqdm
import os
import glob

from simc_test.helpers import make_dir, remove_dir

def get_simc_codes():
    _ = subprocess.getoutput("git clone https://github.com/cimplec/sim-c")

def run_simc_codes():
    test_dir_path = ".simc-test-suite"
    make_dir(test_dir_path)
    os.chdir(test_dir_path)

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
    
    # Set the terminal to default colors
    print("\033[m", end='')

    os.chdir("../../../")
    remove_dir(".simc-test-suite")
