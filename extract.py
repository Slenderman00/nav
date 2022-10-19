import os
import shutil
import subprocess


#process = subprocess.Popen(["python", "setup.py", "build"])
#process.wait()
#print("build complete")

#process = subprocess.Popen(["python", "setup.py", "install"])
#process.wait()
#print("install complete")

os.system("service apache2 stop")

try:
    shutil.rmtree("/opt/venvs/nav/lib/python3.7/site-packages/nav")
except:
    pass

shutil.move("/opt/venvs/nav/lib/python3.7/site-packages/nav-0.1.dev22074+gb477577.d20221018-py3.7.egg/nav", "/opt/venvs/nav/lib/python3.7/site-packages/nav")

shutil.rmtree("/opt/venvs/nav/lib/python3.7/site-packages/nav-0.1.dev22074+gb477577.d20221018-py3.7.egg")

os.system("service apache2 start")

print("donzo")