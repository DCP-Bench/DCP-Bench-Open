# Python-MIP 2.0.0 has no solver of its own: its default solver, CBC, is the library
# that the separate `cbcbox` wheel ships, which mip loads through cffi. The pins are
# the versions pip resolved in the tested image. CBCBOX_BUILD=generic selects the
# non-AVX2 CBC build, so the solver binary does not depend on the host CPU.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
ENV CBCBOX_BUILD=generic
RUN pip install --no-cache-dir mip==2.0.0 cbcbox==2.935 cffi==2.1.1 pycparser==3.11
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/mip_cbc/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
