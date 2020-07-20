import boto3
import os

def dir_maker(loc):
    if not os.path.exists(loc):
        os.mkdir(loc)
        
def file_writer(contents, file):
    if(len(contents) > 0):
        with open(file, 'w') as f:
            f.write(contents)

dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
users_table = dynamodb.Table('bugs')

bugs = users_table.scan()['Items']

root_dir = "code-files"
simc_dir = os.path.join(root_dir, "simc")
c_dir = os.path.join(root_dir, "c")

dir_maker(root_dir)
dir_maker(simc_dir)
dir_maker(c_dir)

for bug in bugs:
    bug_id = str(int(bug['id']))
    simc_code = bug['trigger']
    c_code = bug['c_code']
    
    file_writer(simc_code, os.path.join(simc_dir, bug_id + '.simc'))
    file_writer(c_code, os.path.join(c_dir, bug_id + '.c'))
        