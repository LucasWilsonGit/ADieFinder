import httpx

from RamInfo import *

url = "https://www.msi.com/api/v1/product/support/panel?product=MPG-Z790I-EDGE-WIFI&type=mem&page=1&per_page=1000&id=37&order=desc&column=Supported%20Speed%20(MHz)"

def get_stick_info(json : dict) -> RamInfo:
    info = RamInfo()
    info.vendor = json["Vendor"]
    info.model = json["Model"]
    info.DDR = json["DDR"]
    info.megaherz_base = json["SPD Speed (MHz)"]
    info.chipset = json["Chipset"]
    info.size_GB = f"{json['Size (GB)']}"
    info.process_modelcode()
    return info

json = None
def pull_entries() -> list[RamInfo]:
    global json

    if json == None:
         with httpx.Client(http2=True) as client:
            json = client.get(url).json()

    items : list[dict] = json["result"]["downloads"]["Memory by 13th Gen K series"]["list"]
    infos : list[RamInfo] = [get_stick_info(item) for item in items]
    infos.sort(key = lambda x: x.megaherz_base, reverse=True)
    return infos