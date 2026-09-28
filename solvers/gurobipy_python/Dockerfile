# The gurobipy wheel carries the Gurobi Optimizer and a size-limited licence, so
# this image needs no licence file and no network at run time. That licence stops at 2000 variables and 2000 linear constraints,
# and expires on 2027-11-29. NumPy and SciPy are there for gurobipy's matrix API.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN pip install --no-cache-dir gurobipy==13.0.3 numpy==2.4.6 scipy==1.18.1
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/gurobipy_python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
