"""Runs inside the pumpkin_rust image only. Candidate code never runs on the host.

Compilation is a single `rustc` invocation. The driver library and every Pumpkin
crate are already built into `/opt/rust` at image-build time, so the only crate
compiled here is the one-file submission spliced into `/opt/rust/main.rs`. That
keeps the compile within the evaluator's budget and needs no writable copy of a
Cargo target directory, which matters because `/tmp` is a 512 MiB tmpfs.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import finish

RUSTC = [
    "rustc",
    "--edition", "2021",
    "--crate-name", "candidate",
    "-C", "opt-level=2",
    "-C", "debuginfo=0",
    "-C", "strip=symbols",
    "-C", "codegen-units=1",
    "/opt/rust/main.rs",
    "-o", "/tmp/candidate",
    "--extern", "dcp_pumpkin=/opt/rust/libdcp_pumpkin.rlib",
    "-L", "dependency=/opt/rust/deps",
]


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")
    if not Path("/input/model.rs").is_file():
        return finish("error", "No submission was staged at /input/model.rs")

    before = time.monotonic()
    try:
        result = subprocess.run(RUSTC, stdout=sys.stderr, stderr=sys.stderr,
                                timeout=request["compilation_timeout"])
    except subprocess.TimeoutExpired:
        return finish("compilation_error", "Compilation timed out")
    if result.returncode:
        return finish("compilation_error", "Rust compilation failed; see stderr")
    compile_seconds = time.monotonic() - before
    print(f"Compilation: {compile_seconds:.3f}s", file=sys.stderr)

    # The binary owns the solution/status protocol and its own solve budget; the
    # timeout here is the outer guard for a process that ignores it.
    try:
        result = subprocess.run(["/tmp/candidate"], input=json.dumps(request), text=True,
                                timeout=request["execution_timeout"] + 15)
    except subprocess.TimeoutExpired:
        return finish("timeout", "Rust execution exceeded limit")
    if result.returncode:
        return finish("error", f"Rust process exited {result.returncode}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
