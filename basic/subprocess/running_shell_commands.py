import subprocess

result = subprocess.run("ls", shell=True, capture_output=True, text=True)

print("Args : ", result.args)
print("Return Code : ", result.returncode)
print("Standard Output : ", result.stdout)
print("Standard Error : ", result.stderr)


"""
Result : 
- Args :  ls
- Return Code :  0
- Standard Output :  intorduction.txt
running_shell_commands.py

- Standard Error :  
"""
