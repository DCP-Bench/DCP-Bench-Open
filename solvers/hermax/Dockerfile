FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
# hermax brings its own cardinality and pseudo-Boolean encoders, and pulls
# python-sat in for the SAT and RC2 backends its Model layer solves with.
RUN pip install --no-cache-dir "hermax==1.2.5"
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/hermax/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
