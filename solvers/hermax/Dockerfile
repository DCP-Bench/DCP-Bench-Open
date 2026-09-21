FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
# hermax supplies the MaxSAT solver; python-sat supplies only the cardinality
# and pseudo-Boolean encoders the modelling layer builds clauses with. pypblib
# ships no wheel for 3.12, so it is compiled here and the compiler dropped again.
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 \
 && pip install --no-cache-dir "python-sat[pblib]==1.9.dev15" "hermax==1.2.5" \
 && apt-get purge -y g++ && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/hermax/dcp_maxsat.py /opt/runner/dcp_maxsat.py
COPY solvers/hermax/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
