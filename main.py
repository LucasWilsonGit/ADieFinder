import requests

import msi
import asus
from RamInfo import RamInfo

sticks = msi.pull_entries()
for stick in sticks:
    if stick.chipset in ["SK hynix A", "SK Hynix"]:
        print(stick)#, stick.chipset)