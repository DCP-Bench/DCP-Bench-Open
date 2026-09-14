FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
# Z3 only: runner/runtime.py imports its solver stacks lazily, so this image
# needs none of the shared requirements the CP integrations install.
RUN pip install --no-cache-dir z3-solver==5.1.0.0
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/z3_python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
