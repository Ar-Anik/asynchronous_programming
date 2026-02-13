"""
-> subprocess.Popen is the low-level API of subprocess. It allows full manual control over a running process.
-> subprocess.Popen is useful when more control is needed, such as sending input, receiving output or waiting.
Popen exposes methods and pipes that subprocess.run hides.

"""

"""
With Popen : p = subprocess.Popen(...), the process starts immediately and runs in the background, while the parent
program continues running. This allows:
- Non-blocking execution
- Running multiple processes at the same time
- Monitoring the process while running
"""

"""
# Send input to the process
For programs that expect user input:
"""
import subprocess

p = subprocess.Popen(['python'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

p.stdin.write("print(10+20)\n")
p.stdin.flush()

stdout, stderr = p.communicate()

print("Standard Output : ", stdout)
print("Standard Error : ", stderr)

"""
Popen allows sending input programmatically. subprocess.run() cannot do this (except in simple blocking mode).
"""
