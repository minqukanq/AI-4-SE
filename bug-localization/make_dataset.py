import pandas as pd
import subprocess
import os

projectname = 'eclipse.platform.ui'
Eclipse_Platform_UI = pd.read_excel('dataset/report/' + projectname + '.xlsx', engine='openpyxl')
Eclipse_Platform_UI.rename(columns = {'Unnamed: 10' : 'result'}, inplace = True)

commits = Eclipse_Platform_UI['commit'].values.tolist()
results = Eclipse_Platform_UI['result'].values.tolist()
files = Eclipse_Platform_UI['files'].values.tolist()
print(files[1].split())

git_path = os.path.abspath('dataset\\code\\' + projectname)
cur_path = os.getcwd()
os.chdir(git_path)
print(git_path)
print(files[1].split()[0])
subprocess.call(['cp', files[1].split()[0]], cur_path, shell=True)



# for commit in commits:
#     result = subprocess.call(['git','checkout', commit], shell=True)
    
#     print(result)
#     break


# subprocess.call(['cat', files[1].split()[0]], shell=True)