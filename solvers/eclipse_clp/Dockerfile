# ECLiPSe 7.2 #13 (x86_64 Linux, the basic distribution: kernel, ic, ic_global, gfd,
# fd, branch_and_bound, timeout, lists), checked against its SHA-256 before it is
# unpacked. The eplex LP/MIP interface is not used: its external solvers are not
# installed. Trixie is needed because the 7.2 binary requires GLIBC 2.38.
FROM python:3.12.11-slim-trixie@sha256:47ae396f09c1303b8653019811a8498470603d7ffefc29cb07c88f1f8cb3d19f
ARG ECLIPSE_URL=https://eclipseclp.org/Distribution/Builds/7.2_13/x86_64_linux/eclipse_basic.tgz
ARG ECLIPSE_SHA256=df12d7ab694331f54cd87e5861ceec2ddd41028d1cccf6496ec56ea6755600a3
RUN python -c "import hashlib, sys, urllib.request; \
request = urllib.request.Request(sys.argv[1], headers={'User-Agent': 'curl/8'}); \
data = urllib.request.urlopen(request, timeout=300).read(); \
assert hashlib.sha256(data).hexdigest() == sys.argv[2], 'ECLiPSe archive checksum mismatch'; \
open('/tmp/eclipse.tgz', 'wb').write(data)" "$ECLIPSE_URL" "$ECLIPSE_SHA256" \
 && mkdir -p /opt/eclipse \
 && tar -xzf /tmp/eclipse.tgz -C /opt/eclipse \
 && rm -rf /tmp/eclipse.tgz /opt/eclipse/doc /opt/eclipse/include /opt/eclipse/lib_public/*.jar
ENV ECLIPSEDIR=/opt/eclipse \
    LD_LIBRARY_PATH=/opt/eclipse/lib/x86_64_linux
COPY --chmod=755 runner/runtime.py /opt/runner/runtime.py
COPY --chmod=755 solvers/eclipse_clp/run.py /opt/runner/run.py
COPY --chmod=755 solvers/eclipse_clp/driver.ecl /opt/runner/driver.ecl
ENTRYPOINT ["python3", "/opt/runner/run.py"]
