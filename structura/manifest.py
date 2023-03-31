"""generating manifest.json file"""

import json
from uuid import uuid4


def export(pack_name, zip_file):
    """export manifest.json file"""

    manifest = {
        "format_version": 2,
        "header": {
            "name": pack_name,
            "description": "Structura block overlay pack, created by \u00a7o\u00a75DrAv0011\u00a7r, \u00a7o\u00a79 FondUnicycle\u00a7r and\u00a7o\u00a75 RavinMaddHatter\u00a7r,Improved by MioMiko",
            "uuid": str(uuid4()),
            "version": (0,0,1),
            "min_engine_version": (1,16,0)
        },
        "modules": (
            {
                "type": "resources",
                "uuid": str(uuid4()),
                "version": (0,0,1)},)}

    zip_file.writestr("manifest.json", json.dumps(manifest, indent=2))
