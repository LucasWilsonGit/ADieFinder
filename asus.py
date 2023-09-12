import httpx

from RamInfo import *

url = "https://rog.asus.com/support/webapi/product/GetPDQVLMemory?website=global&model=rog-maximus-z790-apex&pdid=0&m1id=21152&mode=&PageSize=1000&PageIndex=1&keyword=&CPUSeries=13th+Gen+Intel®+Core™+(K%2FKF+series)&systemCode=rog"

def get_stick_info(json : dict) -> RamInfo:
    info = RamInfo()

    info.vendor = json["Vendors"]
    info.model = json["PartNo"]
    info.megaherz_base = json["RAMSpeed"]
    info.chipset = json["ChipBrand"]   #Only specifies the brand and not which specific IC so it's a bit useless isn't it? 
    info.timings = json["Timing"]
    info.size_GB = (json["Size"]).replace("GB", "")
    info.process_modelcode()
    return info

json = None
def pull_entries() -> list[RamInfo]:
    global json

    if json == None:
        with httpx.Client(http2=True) as client:
            json = client.get(url).json()

    items : list[dict] = json["Result"]["Obj"]
    infos : list[RamInfo] = [get_stick_info(item) for item in items]
    infos.sort(key = lambda x: x.megaherz_base)
    return infos