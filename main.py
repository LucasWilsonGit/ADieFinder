import requests

import msi
import asus#only knows the brand of chip, not which specific chip i.e SK Hynix [A die (this is missing in the ASUS dataset)]
from RamInfo import RamInfo, match_sticks, FilterEntry



sticks = msi.pull_entries()
filter = {
    "vendor" : FilterEntry("in", ["CORSAIR", "Kingston", "Team Group", "TEAM GROUP", "T-FORCE"]),
    "megaherz_base" : FilterEntry(">=", 6400),
    #"chipset" : FilterEntry("in", ["SK hynix A"])
}

for stick in match_sticks(sticks, filter):
    print(stick)