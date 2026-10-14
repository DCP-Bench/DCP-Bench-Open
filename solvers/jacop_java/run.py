"""Runs inside the jacop_java image only. Candidate code never runs on the host.

A submission is one Java file declaring a class `Submission` with
`static Model build(JSONObject instance, Store store)`. It is compiled with one
`javac` call against JaCoP, org.json and the harness jar baked into the image,
then `dcp.jacop.Runner` loads it, solves, and owns the JSONL protocol on stdout.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import finish

CLASSPATH = "/opt/jacop/jacop.jar:/opt/jacop/json.jar:/opt/jacop/dcp-jacop.jar"
# One CPU, a 128-process cap and a read-only root: a serial collector, few JIT
# threads and no perf-data file under /tmp keep the JVM inside all three.
JVM = ["-XX:+UseSerialGC", "-XX:CICompilerCount=2", "-XX:-UsePerfData", "-XX:MaxRAMPercentage=75",
       "-Xss256m", "-Djava.io.tmpdir=/tmp"]


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")
    if not Path("/input/model.java").is_file():
        return finish("error", "No submission was staged at /input/model.java")

    # A public class has to live in a file of its own name, so the submission
    # is copied to Submission.java before compiling.
    source = Path("/tmp/src/Submission.java")
    source.parent.mkdir(parents=True)
    shutil.copyfile("/input/model.java", source)
    before = time.monotonic()
    command = ["javac", *(f"-J{flag}" for flag in JVM[:3]), "-encoding", "UTF-8", "-nowarn",
               "-cp", CLASSPATH, "-d", "/tmp/classes", str(source)]
    try:
        result = subprocess.run(command, stdout=sys.stderr, stderr=sys.stderr,
                                timeout=request["compilation_timeout"])
    except subprocess.TimeoutExpired:
        return finish("compilation_error", "Compilation timed out")
    if result.returncode:
        return finish("compilation_error", "Java compilation failed; see stderr")
    if not Path("/tmp/classes/Submission.class").is_file():
        return finish("compilation_error", "The submission declares no top-level class Submission")
    print(f"Compilation: {time.monotonic() - before:.3f}s", file=sys.stderr)

    # The runner owns the solution/status protocol and its own solve budget; the
    # timeout here is the outer guard for a search that ignores it.
    try:
        result = subprocess.run(["java", *JVM, "-cp", f"/tmp/classes:{CLASSPATH}", "dcp.jacop.Runner"],
                                input=json.dumps(request), text=True,
                                timeout=request["execution_timeout"] + 5)
    except subprocess.TimeoutExpired:
        return finish("timeout", "Java execution exceeded limit")
    if result.returncode:
        return finish("error", f"Java process exited {result.returncode}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
