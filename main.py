import requests

import gigabyte
import msi
import asus#only knows the brand of chip, not which specific chip i.e SK Hynix [A die (this is missing in the ASUS dataset)]
from RamInfo import RamInfo, match_sticks, FilterEntry



sticks = gigabyte.pull_entries()
filter = {
    "chipset"   : FilterEntry("in", ["Hynix M", "SK Hynix", "SK Hynix M", "SK hynix M"]),
    "size_GB"      : FilterEntry("==", "16")
    #"product_line" : FilterEntry("==", "T-CREATE")
}
sticks = match_sticks(sticks, filter)
for stick in sticks:
    print(stick, stick.timings)