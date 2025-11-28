import subprocess

p = subprocess.Popen(['python', 'slow_output.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print("Reading Output Line by Line :")
for line in p.stdout:
    print("Line Received :", line.strip())

p.wait()

"""
Q : What p.wait() actually does?
p.wait() performs two critical actions:
- Blocks the parent program until the child process finishes execution
- Collects the child’s exit status from the operating system
- Reaps the process (prevents zombie processes on Unix/macOS)

After p.wait() returns:
- The child process has exited
- The exit code is stored in p.returncode
- The OS resources for that process are fully released
"""
