"""Run every example of a skill's assets/ folder inside the image and print its stdout."""
import os
import subprocess
import sys

IMAGE = sys.argv[1]
ASSETS = sys.argv[2]
for name in sorted(os.listdir(ASSETS)):
    folder = os.path.join(ASSETS, name)
    if not os.path.isdir(folder):
        continue
    result = subprocess.run(
        ["docker", "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}",
         "-e", "HOME=/tmp", "-v", f"{folder}:/w:ro", "-w", "/w", "--entrypoint", "python",
         IMAGE, "model.py"],
        capture_output=True, text=True, timeout=300)
    print(f"== {name}: exit {result.returncode}")
    print(result.stdout.rstrip())
    if result.returncode:
        print("stderr:", result.stderr.strip().splitlines()[-1:])
