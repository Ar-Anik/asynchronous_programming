import subprocess
import sys

result = subprocess.run([sys.executable, "-c", "print('Hi Aubdur Rob Anik')"], capture_output=True, text=True)

"""
Here sys.executable indicate current python interpreter path.
-c instruction that run the string as python code instead a script.
"""

print(result.args)
print(result.returncode)
print(result.stdout)
print(result.stderr)

"""
Reuslt : 
['/usr/local/bin/python3.13', '-c', "print('Hi Aubdur Rob Anik')"]
0
Hi Aubdur Rob Anik
"""