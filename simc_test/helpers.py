import os
import shutil

def remove_dir(dir_path):
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except:
            _ = subprocess.getoutput(f'rd /s /q "{dir_path}"')

def make_dir(dir_path):
    if os.path.exists(dir_path):
        remove_dir(dir_path)
        
    os.mkdir(dir_path)