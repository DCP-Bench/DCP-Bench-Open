#!/bin/bash
# Inspection of the probe image: installed packages and the cbcbox binary's CBC version.
IMG=dcp-probe/mip_cbc:2.0.0
docker run --rm --network none --entrypoint pip "$IMG" freeze
docker run --rm --network none --entrypoint python "$IMG" -c "import cbcbox,os; d=os.path.dirname(cbcbox.__file__); print(d); print(sorted(os.listdir(d)))"
docker run --rm --network none --entrypoint python "$IMG" -c "import mip.cbc as c; print([n for n in dir(c.cbclib) if 'ersion' in n])"
docker run --rm --network none --entrypoint python "$IMG" -c "import mip.cbc as c; print(c.cbclib.Cbc_getVersion() if hasattr(c.cbclib,'Cbc_getVersion') else 'no Cbc_getVersion')"
