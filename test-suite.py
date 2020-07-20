import git
import tempfile
import shutil
import os
import glob
import subprocess

def copytree(src, dst, symlinks=False, ignore=None):

    """
    Copies a folder with all files and subfolder to one position to another
    Params
    ======
        src (str): Source folder
        dst (str): Destination folder
    """

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
            
def file_content_matches(file1, file2):
    if not os.path.exists(file1) or not os.path.exists(file2):
        return -1
    
    with open(file1, 'r') as f:
        data1 = f.read()
    
    with open(file2, 'r') as f:
        data2 = f.read()
        
    return 0 if data1 == data2 else -1

if os.path.exists('code-files'):
    shutil.rmtree('code-files')

print("Step (1) Cloning the test programs into system.")
t = tempfile.mkdtemp()
git.Repo.clone_from('https://github.com/cimplec/sim-c.git', t, branch='tests', depth=1)
copytree(t, '.')
shutil.rmtree('.git')
os.remove('.gitignore')

print("Step (2) Testing code.")

simc_files = glob.glob("code-files/simc/*.simc")
c_files = glob.glob("code-files/c/*.c")

correct = 0
failed = 0
unknown = 0

correct_files_index = []

for i in range(len(simc_files)):
    c_code_file = os.path.join('code-files/c', os.path.basename(simc_files[i]).split('.simc')[0] + '.c')
    if not os.path.exists(c_code_file):
        unknown += 1
        continue
    
    simc_output = subprocess.getoutput('python ../sim-c/simc.py %s' % simc_files[i])
    c_in_simc_dir_path = os.path.join('code-files/simc/', os.path.basename(c_code_file))
    
    if(file_content_matches(c_code_file, c_in_simc_dir_path) == 0):
        correct += 1
        correct_files_index.append(simc_files[i])
    else:
        failed += 1
        
c_in_simc_files = glob.glob('code-files/simc/*.c')

for file in c_in_simc_files:
    os.remove(file)
    
print()
print(u"Tests passed \U0001F600 [%d/%d]" % (correct, len(simc_files)))
print()
print(u"Tests failed \U0001F622 [%d/%d]" % (failed, len(simc_files)))
print()
print(u"Unknown results \U0001F914 [%d/%d]" % (unknown, len(simc_files)))