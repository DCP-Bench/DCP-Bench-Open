#!/bin/bash
# CBC version: run the bundled cbc binary with -quit and grep for its banner; also list version files.
IMG=dcp-probe/mip_cbc:2.0.0
docker run --rm --network none --entrypoint sh "$IMG" -c 'B=/usr/local/lib/python3.12/site-packages/cbcbox/cbc_dist_avx2/bin/cbc; ls /usr/local/lib/python3.12/site-packages/cbcbox/cbc_dist_avx2/bin; $B -quit 2>&1 | head -5; $B -version 2>&1 | head -5; grep -rIl -i "version" /usr/local/lib/python3.12/site-packages/cbcbox/cbc_dist_avx2/share 2>/dev/null | head -5'
docker run --rm --network none --entrypoint sh "$IMG" -c 'B=/usr/local/lib/python3.12/site-packages/cbcbox/cbc_dist/bin/cbc; $B -quit 2>&1 | head -3; grep -a -o "Cbc[ _]Version[^\"]\{0,20\}\|CoinUtils[^\"]\{0,15\}" /usr/local/lib/python3.12/site-packages/cbcbox/cbc_dist/lib/libCbc.so.0.0.0 2>/dev/null | head -5'
