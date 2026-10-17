"""Run one submission through the mip_cbc image the way the evaluator does.

usage: case.py MODEL.py '{"instance": {...}, "solution_limit": 1, "execution_timeout": 10}'
Copies the model into a fresh directory as /input/model.py with a request.json, mounts it
read-only at /input, runs the image with no network and prints stdout, stderr and exit code.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

IMAGE = "dcp-eval/mip_cbc:v1"


def main():
    model_path, request_text = sys.argv[1], sys.argv[2]
    request = json.loads(request_text)
    request.setdefault("solution_limit", 1)
    request.setdefault("execution_timeout", 10)
    request.setdefault("compilation_timeout", 10)
    request.setdefault("legacy", False)
    request.setdefault("instance", {})
    with tempfile.TemporaryDirectory(prefix="mipcase_") as directory:
        shutil.copy(model_path, os.path.join(directory, "model.py"))
        with open(os.path.join(directory, "request.json"), "w") as handle:
            json.dump(request, handle)
        os.chmod(directory, 0o755)
        for name in ("model.py", "request.json"):
            os.chmod(os.path.join(directory, name), 0o644)
        command = ["docker", "run", "--rm", "--network", "none", "--read-only",
                   "--tmpfs", "/tmp:size=512m", "--user", "65534:65534",
                   "-v", f"{directory}:/input:ro", IMAGE]
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=request["execution_timeout"] + 60)
    print("exit", result.returncode)
    print("stdout:")
    print(result.stdout.rstrip())
    print("stderr (tail):")
    print("\n".join(result.stderr.rstrip().splitlines()[-8:]))


if __name__ == "__main__":
    main()
