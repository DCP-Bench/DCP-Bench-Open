# PuLP ships the CBC binary it calls, so this image installs one wheel and needs
# nothing else at run time.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN pip install --no-cache-dir pulp==3.3.2
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/pulp_cbc/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
