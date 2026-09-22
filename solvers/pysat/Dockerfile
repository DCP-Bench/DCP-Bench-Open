FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
# pypblib, which python-sat needs for its pseudo-Boolean encoders, ships no
# wheel for 3.12, so it is compiled here and the compiler is dropped again.
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 \
 && pip install --no-cache-dir "python-sat[pblib]==1.9.dev15" \
 && apt-get purge -y g++ && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/pysat/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
