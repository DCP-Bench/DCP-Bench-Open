# PyCSP3 2.6.1 (Python modelling) to XCSP3 and the ACE-2.6 solver, which ships
# inside the pycsp3 wheel and needs a Java runtime (ACE class files are Java 8/11).
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
 && rm -rf /var/lib/apt/lists/*
COPY solvers/pycsp3_ace/requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r /opt/requirements.txt
# Java: keep temporary files and the heap inside the tmpfs /tmp and the 2048 MiB limit.
ENV JAVA_TOOL_OPTIONS="-Xmx1200m -XX:-UsePerfData -Djava.io.tmpdir=/tmp"
COPY --chmod=0755 runner/runtime.py /opt/runner/runtime.py
COPY --chmod=0755 solvers/pycsp3_ace/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
