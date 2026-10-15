FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
# idp-engine pins its own z3-solver (4.11.2.0) and pulls sli-lib, a Rust
# extension shipped only as a cp311-abi3 manylinux_2_28 wheel; bookworm's glibc
# 2.36 satisfies it, so nothing has to be compiled.
RUN pip install --no-cache-dir idp-engine==0.12.1
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/idp_z3/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
