# PySCIPOpt wraps SCIP 10.0.2, which ships inside the wheel; NumPy is the only
# Python dependency. Both are pinned by hash in requirements.txt, and the install
# accepts binary wheels only, so nothing is compiled inside the image.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
COPY solvers/scip_python/requirements.txt /opt/runner/requirements.txt
RUN pip install --no-cache-dir --only-binary :all: --require-hashes -r /opt/runner/requirements.txt
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/scip_python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
