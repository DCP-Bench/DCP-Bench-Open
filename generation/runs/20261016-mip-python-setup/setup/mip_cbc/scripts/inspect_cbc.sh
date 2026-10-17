#!/bin/bash
# Find the CBC version string inside the cbcbox binary distribution.
IMG=dcp-probe/mip_cbc:2.0.0
docker run --rm --network none --entrypoint sh "$IMG" -c 'D=/usr/local/lib/python3.12/site-packages/cbcbox; cat $D/__init__.py | head -60; ls -la $D/cbc_dist $D/cbc_dist_avx2 | head -30'
docker run --rm --network none --entrypoint sh "$IMG" -c 'D=/usr/local/lib/python3.12/site-packages/cbcbox; for f in $(find $D -name "*.so*" -o -name "cbc*" -type f | head -20); do echo "== $f"; strings "$f" | grep -i -m3 "Cbc.*version\|version.*2\.10\|CBC Version\|Cbc Version\|2\.10\.[0-9]"; done'
