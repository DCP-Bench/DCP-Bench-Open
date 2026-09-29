# Picat 3.9#12, the official 64-bit Linux build from picat-lang.org, checked
# against its SHA-256 before it is unpacked. It is one static-enough binary plus
# its library modules, which include the cp and sat solvers a submission imports;
# the manual and examples are dropped. Python runs the runner around it.
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
ARG PICAT_URL=https://picat-lang.org/download/picat39_12_linux64.tar.gz
ARG PICAT_SHA256=f053b11cccabfb69a3ccd779f2dc1c24cdf889805799bc8c779e6c56da703e4a
RUN python -c "import hashlib, sys, urllib.request; \
data = urllib.request.urlopen(sys.argv[1], timeout=300).read(); \
assert hashlib.sha256(data).hexdigest() == sys.argv[2], 'Picat archive checksum mismatch'; \
open('/tmp/picat.tar.gz', 'wb').write(data)" "$PICAT_URL" "$PICAT_SHA256" \
 && tar -xzf /tmp/picat.tar.gz -C /opt \
 && mv /opt/Picat /opt/picat \
 && rm -rf /tmp/picat.tar.gz /opt/picat/doc /opt/picat/exs \
 && /opt/picat/picat --version
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/picat/run.py /opt/runner/run.py
COPY solvers/picat/driver.pi /opt/runner/driver.pi
ENTRYPOINT ["python", "/opt/runner/run.py"]
