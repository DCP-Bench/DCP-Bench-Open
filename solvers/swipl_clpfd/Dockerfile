# The official SWI-Prolog image already carries library(clpfd), library(http/json)
# and a Python interpreter, so this integration installs nothing of its own.
FROM swipl:9.2.9@sha256:3e4b85b16f1e269c8a3ce3d968c843aa4cd858f7ace2db49398ec9a2b113bf0f
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/swipl_clpfd/run.py /opt/runner/run.py
COPY solvers/swipl_clpfd/driver.pl /opt/runner/driver.pl
ENTRYPOINT ["python3", "/opt/runner/run.py"]
