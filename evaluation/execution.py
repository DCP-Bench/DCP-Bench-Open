"""Resource-bounded Docker execution. No implicit builds or dependency installation."""
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import uuid

from .results import EvaluationError, strict_json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LIMIT = 8 * 1024 * 1024


def run_process(command, timeout, input_bytes=None):
    """Drain both pipes with bounded memory, including malicious/noisy programs."""
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        raise EvaluationError("infrastructure_error", str(e)) from e
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()

    def drain(pipe, buffer):
        while chunk := pipe.read(65536):
            remaining = OUTPUT_LIMIT - len(buffer)
            buffer.extend(chunk[:max(0, remaining)])
            if len(chunk) > remaining:
                overflow.set()
                process.kill()
        pipe.close()

    threads = [threading.Thread(target=drain, args=(pipe, buffer), daemon=True)
               for pipe, buffer in zip((process.stdout, process.stderr), buffers)]
    for thread in threads:
        thread.start()
    if input_bytes is not None:
        try:
            process.stdin.write(input_bytes)
            process.stdin.close()
        except BrokenPipeError:
            pass
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        process.kill()
        process.wait()
        raise EvaluationError("execution_timeout", f"Process exceeded {timeout} seconds") from e
    finally:
        for thread in threads:
            thread.join(5)
    if overflow.is_set():
        raise EvaluationError("output_limit", "Runner output exceeded 8 MiB")
    return process.returncode, *(b.decode("utf-8", errors="replace") for b in buffers)


def integration(solver_id):
    if not isinstance(solver_id, str) or not solver_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in solver_id):
        raise EvaluationError("unsupported_solver", "Use an installed solver integration ID")
    path = ROOT / "solvers" / solver_id / "metadata.yaml"
    if not path.is_file():
        raise EvaluationError("unsupported_solver", f"No integration: {solver_id}")
    # JSON is a YAML subset; avoids a YAML dependency in the orchestration package.
    metadata = strict_json(path.read_text(encoding="utf-8"))
    if metadata["id"] != solver_id:
        raise EvaluationError("infrastructure_error", "Integration metadata ID mismatch")
    return metadata


def image_identity(metadata):
    code, stdout, stderr = run_process(["docker", "image", "inspect", metadata["image"], "--format", "{{.Id}}"], 15)
    if code:
        raise EvaluationError("infrastructure_error", f"Image unavailable; start Docker and explicitly build {metadata['id']}. {stderr.strip()}")
    identity = stdout.strip()
    if not identity.startswith("sha256:"):
        raise EvaluationError("infrastructure_error", "Docker did not return an image identity")
    return identity


def killed_for_memory(name):
    """Whether the kernel killed any process in the exited container at its memory limit.

    Docker sets this for the runner and for a solver process the runner started
    alike, and exit 137 alone cannot tell it apart from a SIGKILL a submission
    sent itself.
    """
    code, stdout, stderr = run_process(["docker", "inspect", "--format", "{{.State.OOMKilled}}", name], 15)
    if code or stdout.strip() not in ("true", "false"):
        raise EvaluationError("infrastructure_error", f"Could not inspect container {name}: {stderr.strip()}")
    return stdout.strip() == "true"


def execute(model_path, instance, metadata, image, *, solution_limit, execution_timeout,
            compilation_timeout, memory_mb, cpus, legacy=False, model_bytes=None, outputs=None):
    name = "dcp-eval-" + uuid.uuid4().hex
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="dcp_candidate_") as temp:
        staging = Path(temp)
        # tempfile directories are 0700 on Linux; the unprivileged container must
        # be able to traverse this dedicated directory (never its host parent).
        staging.chmod(0o755)
        # Only the entrypoint is copied. Never mount its parent (which may contain references/secrets).
        (staging / ("model" + metadata["extension"])).write_bytes(
            Path(model_path).read_bytes() if model_bytes is None else model_bytes)
        # The declared output names, so a runner can map its own naming back to
        # them. They are already in the brief the modeller works from, so this
        # tells a submission nothing it should not know, and never a solution.
        request = {"instance": instance, "solution_limit": solution_limit,
                   "execution_timeout": execution_timeout, "compilation_timeout": compilation_timeout,
                   "legacy": legacy, "outputs": list(outputs or [])}
        (staging / "request.json").write_text(json.dumps(request, allow_nan=False), encoding="utf-8")
        for path in staging.iterdir():
            path.chmod(0o644)
        # No --rm: the container has to outlive its exit so killed_for_memory can
        # inspect it. The finally clause below removes it.
        command = ["docker", "run", "--pull=never", "--name", name,
                   "--network=none", "--read-only", "--user=65534:65534", "--cap-drop=ALL",
                   "--security-opt=no-new-privileges", "--pids-limit=128", "--log-driver=none",
                   "--memory", f"{memory_mb}m", "--memory-swap", f"{memory_mb}m", "--cpus", str(cpus),
                   "--tmpfs", "/tmp:rw,exec,nosuid,size=536870912,mode=1777",
                   "--mount", f"type=bind,source={staging},target=/input,readonly",
                   "--workdir=/tmp", "--env=HOME=/tmp", "--env=PYTHONDONTWRITEBYTECODE=1", image]
        budget = execution_timeout + (compilation_timeout if metadata.get("compilation", False) else 0) + 10
        try:
            code, stdout, stderr = run_process(command, budget)
            try:
                oom_killed = killed_for_memory(name)
            except EvaluationError as error:
                raise EvaluationError(error.reason, f"{error.detail}; the run exited {code}: {stderr[-4000:]}") from error
            if code:
                if oom_killed:
                    raise EvaluationError("memory_limit", f"The kernel killed a process at the {memory_mb} MB "
                                                          f"memory limit and the runner exited {code}: {stderr[-4000:]}")
                raise EvaluationError("execution_error", f"Runner exited {code}: {stderr[-4000:]}")
            try:
                records = [strict_json(line) for line in stdout.splitlines() if line.strip()]
            except (ValueError, TypeError, RecursionError) as e:
                raise EvaluationError("invalid_output", f"Malformed runner JSON: {e}") from e
            return records, {"execution_wall_seconds": time.perf_counter() - started, "stderr": stderr[-4000:],
                             "oom_killed": oom_killed}
        finally:
            # docker-client termination alone does not terminate the container.
            try:
                code, _, detail = run_process(["docker", "rm", "--force", name], 15)
                if code and "No such container" not in detail:
                    raise EvaluationError("infrastructure_error", f"Container cleanup failed for {name}: {detail}")
            except EvaluationError as error:
                raise EvaluationError("infrastructure_error", f"Could not confirm cleanup of {name}: {error}") from error


def validate_records(records):
    if not records or not all(isinstance(x, dict) for x in records):
        raise EvaluationError("invalid_output", "Expected runner JSON records")
    if records[-1].get("type") != "status" or any(x.get("type") != "solution" for x in records[:-1]):
        raise EvaluationError("invalid_output", "Expected solution records followed by exactly one status")
    status = records[-1]
    if status.get("status") not in ("complete", "limit", "timeout", "unsat", "error", "unsupported", "compilation_error"):
        raise EvaluationError("invalid_output", "Unknown runner status")
    return [x.get("values") for x in records[:-1]], status
