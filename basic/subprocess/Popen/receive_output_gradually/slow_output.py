import time

for i in range(1, 10):
    print(f"Output line {i}", flush=True)
    time.sleep(1)

"""
- Prints one line every 1 second
- flush=True forces Python to send output immediately to the pipe
- Without flush=True, output may be delayed due to buffering
"""
