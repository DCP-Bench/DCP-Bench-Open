"""Runs inside the maxicp_java image only. Candidate code never runs on the host.

The submission is one Java file declaring `public class Submission` with
`public static void build(Instance inst, Model model, Outputs out)`. It is
compiled with javac against MaxiCP, Gson and the prebuilt driver in
/opt/java/dcp.jar, then dcp.Main runs it and owns the runner protocol.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import finish

CLASSPATH = "/opt/java/dcp.jar:/opt/java/maxicp.jar:/opt/java/gson.jar"
# One CPU, 2 GiB and 128 processes in the container: a single-threaded JVM
# with a serial collector, and heap left below the limit so an exhausted heap
# ends as an OutOfMemoryError the driver reports rather than a kernel kill.
JVM = ["-XX:+UseSerialGC", "-XX:ActiveProcessorCount=1", "-XX:-UsePerfData", "-Xshare:auto"]
JAVAC = ["javac", "-J-XX:+UseSerialGC", "-J-XX:ActiveProcessorCount=1", "-J-XX:TieredStopAtLevel=1",
         "-J-XX:-UsePerfData", "-J-Xmx512m", "-encoding", "UTF-8", "-nowarn", "-cp", CLASSPATH,
         "-d", "/tmp/classes", "/tmp/src/Submission.java"]
RUN = ["java", *JVM, "-Xmx1400m", "-Xss256m", "-cp", "/tmp/classes:" + CLASSPATH, "dcp.Main"]


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")
    if not Path("/input/model.java").is_file():
        return finish("error", "No submission was staged at /input/model.java")
    # javac requires a public class to live in a file of its own name.
    Path("/tmp/src").mkdir()
    Path("/tmp/classes").mkdir()
    shutil.copyfile("/input/model.java", "/tmp/src/Submission.java")

    before = time.monotonic()
    try:
        result = subprocess.run(JAVAC, stdout=sys.stderr, stderr=sys.stderr, timeout=request["compilation_timeout"])
    except subprocess.TimeoutExpired:
        return finish("compilation_error", "Compilation timed out")
    if result.returncode:
        return finish("compilation_error", "Java compilation failed; see stderr")
    print(f"Compilation: {time.monotonic() - before:.3f}s", file=sys.stderr)

    # The driver owns the solution/status protocol and its own deadline; the
    # timeout here is the outer guard for a process that ignores it.
    try:
        result = subprocess.run(RUN, input=json.dumps(request), text=True,
                                timeout=request["execution_timeout"] + 15)
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
