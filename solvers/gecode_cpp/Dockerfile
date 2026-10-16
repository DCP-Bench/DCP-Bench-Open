
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 nlohmann-json3-dev=3.11.2-2 libgecode-dev=6.2.0-5 && rm -rf /var/lib/apt/lists/*
COPY --chmod=0755 solvers/gecode_cpp/cpp /opt/cpp
COPY --chmod=0755 runner/runtime.py solvers/gecode_cpp/run.py /opt/runner/
ENTRYPOINT ["python", "/opt/runner/run.py"]
