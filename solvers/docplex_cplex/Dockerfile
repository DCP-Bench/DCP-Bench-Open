# The cplex wheel is the CPLEX Community Edition: the optimizer and its licence
# in one package, with no licence file and no network needed at run time. It
# stops at 1000 variables and 1000 constraints. DOcplex is IBM's modelling API
# on top of it, and the one a submission writes against.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN pip install --no-cache-dir cplex==22.2.0.1 docplex==2.32.264
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/docplex_cplex/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
