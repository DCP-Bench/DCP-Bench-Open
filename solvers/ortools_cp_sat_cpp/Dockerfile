FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 curl=7.88.1-10+deb12u15 ca-certificates=20250419~deb12u1 nlohmann-json3-dev=3.11.2-2 && rm -rf /var/lib/apt/lists/*
RUN curl -fL https://github.com/google/or-tools/releases/download/v9.15/or-tools_amd64_debian-12_cpp_v9.15.6755.tar.gz -o /tmp/ortools.tgz && echo 'b2c9870c8778eeb26c98742402da17da039c058fca7eca87be5c90832b04153c  /tmp/ortools.tgz' | sha256sum -c - && mkdir /opt/ortools && tar xzf /tmp/ortools.tgz -C /opt/ortools --strip-components=1 && rm /tmp/ortools.tgz
COPY solvers/ortools_cp_sat_cpp/cpp /opt/cpp
ENV CMAKE_PREFIX_PATH=/opt/ortools
ENV LD_LIBRARY_PATH=/opt/ortools/lib
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/ortools_cp_sat_cpp/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
