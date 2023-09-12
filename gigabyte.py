import httpx, re
from RamInfo import *

url = "https://www.gigabyte.com/Ajax/SupportFunction/GetMemorySupportTable"


html = ""
def pull_entries() -> list[RamInfo]:
    global html

    if html == "":
        #gigabyte's API just chunk loads the whole thing in HTML table form this is why the page takes like 30 seconds to load lmao what are these guys doing
        with httpx.Client(http2=True) as client:
            with client.stream("POST", url, headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Content-Length" : "7"
            },
            content="id=8678") as response:
                total = int(response.headers["Content-Length"])
                for chunk in response.iter_bytes():
                    decoded = chunk.decode()
                    if decoded != None:
                        html += decoded
        
    table_post = """</table>"""

    #print(html)
    body_defs = html.split("""<table class="memory-support-table nowrap" """)[1].split("</table>")[0].split("<tbody>")[1].split("<tr>")
    infos : list[RamInfo] = []
    for tbl in body_defs[1:]:
        rows = tbl.split("<td")
        rows = [ re.sub("d.*?>", "", row).replace("</t", "").replace("\r\n","").rstrip(" ")[1:] for row in rows ]

        speed = rows[1]
        vendor = rows[2]
        size = rows[3].replace("GB", "")
        model=rows[5]
        chipset=rows[7]
        timing=rows[8]

        info = RamInfo()
        info.vendor = vendor
        info.model = model
        info.size_GB = size
        info.megaherz_base = speed
        info.chipset = chipset
        info.timings = timing
        info.DDR = "DDR5"
        infos.append(info)

    infos.sort(key = lambda x: x.megaherz_base, reverse=False)
    return infos