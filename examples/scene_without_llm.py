"""Create a holed solid with a detached component; write the Maslov geometry to stdout."""

import json

from text2bim_massing import MassingTools, Scene

scene = Scene()
tools = MassingTools(scene, units="mm")
profile = tools.create_profile(
    [
        [(0, 0), (10000, 0), (10000, 10000), (0, 10000)],
        [(2000, 2000), (2000, 4000), (4000, 4000), (4000, 2000)],
        [(20000, 0), (24000, 0), (24000, 4000), (20000, 4000)],
    ]
)
solid = tools.create_extrusion(profile, 0, 6000)
copy = tools.duplicate_obj(solid)[0]
tools.move_obj(copy, yDistance=15000)
print(json.dumps(tools.export_massing(), indent=2))
