import requests

import gigabyte
import msi
import asus#only knows the brand of chip, not which specific chip i.e SK Hynix [A die (this is missing in the ASUS dataset)]
from RamInfo import RamInfo, match_sticks, FilterEntry



sticks = msi.pull_entries()
filter = {
    "chipset"   : FilterEntry("in", ["Hynix A", "SK Hynix", "SK Hynix A", "SK hynix A"]),
    "size_GB"      : FilterEntry("==", "16")
    #"product_line" : FilterEntry("==", "T-CREATE")
}
sticks = match_sticks(sticks, filter)
for stick in sticks:
    print(stick, stick.timings)