import operator
from typing import Any, Callable

class ModelReader:
    position : int = 0
    model_code : str = ""
    def __init__(self, model_code : str):
        self.model_code = model_code

    def read(self, char_count : int) -> str:
        if char_count == 0:
            return ""
        
        res = self.model_code[self.position:self.position + char_count]
        self.position += char_count
        return res
    
    def read_until_any(self, chars : str, maxread=500) -> str:
        """searches through the string until it finds a character in the string chars"""

        for x in range(maxread):
            if self.model_code[self.position+x] in chars:
                return self.read(x)

        return ""
    
    def read_until(self, char : str) -> str:
        assert len(char)==1, "Length must be 1 char"
        return self.read_until_any(char)
    
    def read_remaining(self) -> str:
        res = self.model_code[self.position:]
        self.position = 0
        return res
    
    def step(self, count : int) -> None:
        """
        steps the reader head by count chars
        """
        self.position += count





class RamInfo:
    vendor          : str = "Unknown",
    model           : str = "Unknown",
    DDR             : str = "Unknown",
    megaherz_base   : str = "Unknown",
    chipset         : str = "Unknown",
    size_GB         : str = "Unknown",
    timings         : str = "Unknown"
    
    def __proc_teamgroup(self, model_code : str) -> None:
        """
        decodes the aprt name by teamgroup spec
        https://www.teamgroupinc.com/en/info/ins.php?index_id=90
        FF4D532G7800HC36DDC01
        """
        reader = ModelReader(model_code)
        
        product_line = reader.read(1)
        product_meta = reader.read_until("D")
        reader.step(1)
        
        self.DDR=f"DDR{reader.read(1)}"
        self.size_GB=reader.read_until('G')
        reader.step(1)
        self.megaherz_base=reader.read_until_any("HC")
        
        heatsink = reader.read(1)
        if heatsink == "H":
            heatsink = "Heatsink"
        else:
            heatsink = "No heatsink"
            reader.step(-1)
        
        timings = reader.read_until_any("DQO -S0B")
        timings_map = {
            "C28"   : "28-34-34-76",
            "C30"   : "30-36-36-76",
            "C32"   : "32-36-36-76",
            "C32A"  : "32-39-39-84",
            "C32B"  : "32-39-39-76",
            "C34"   : "34-40-40-84",
            "C34A"  : "34-42-42-84",
            "C34B"  : "34-44-44-84",
            "C36"   : "36-36-36-77",
            "C36A"  : "36-36-36-75",
            "C36B"  : "36-36-36-76",
            "C36C"  : "36-44-44-84",
            "C36D"  : "36-46-46-84",
            "C36E"  : "36-47-47-84",
            "C38"   : "38-38-38-84",
            "C38A"  : "38-38-38-78",
            "C38B"  : "38-44-44-76",
            "C38C"  : "38-40-40-84",
            "C38D"  : "38-48-48-84",
            "C38E"  : "38-49-49-84",
            "C38F"  : "38-38-38-70",
            "C40"   : "40-40-40-77",
            "C40A"  : "40-40-40-80",
            "C40B"  : "40-40-40-84",
            "C40C"  : "40-40-40-76",
            "C42"   : "42-42-42-84",
            "C46"   : "46-46-46-90",
            "C48"   : "48-48-48-96"
        }
        self.timings = timings_map.get(timings, 1)
    
    def __proc_kingston(self, model_code : str) -> None:
        """
        decodes the part name by spec of Kingston kits
        https://www.kingston.com/unitedkingdom/en/memory/memory-part-number-decoder
        """
        reader = ModelReader(model_code)

        maker = reader.read(2)
        if maker != "KF":
            #I DO NOT SUPPORT ANYTHING THAT ISNT KINGSTON FURY THERE IS TOO MUCH STUFF HAHA
            #TODO: make submethods for Kingston Fury, Kingston Value DRAM, Kingston design-in
            return

        self.DDR = f"DDR{reader.read(1)}"
        self.megaherz_base = f"{reader.read_until_any('CSR')}00"

        #these are unused for now
        module_type = reader.read(1)
        subtiming = reader.read(2)
        series = reader.read(1)
        color = reader.read(1)
        profile_type = reader.read(1)
        if profile_type == "E":
            profile_type = "AMD EXPO"
        else:
            profile_type = "XMP"
            reader.step(-1)
        revision = reader.read(1)
        if revision not in ["2", "3", "4"]:
            reader.step(-1)
            revision = "1"

        rgb = reader.read(1)
        if rgb == "-":
            reader.step(-1)
            rgb=""
        else:
            map = {
                "A" : "RGB"
            }
            rgb = map.get(rgb,"")

        stick_count = reader.read(1)
        if stick_count == "K":
            stick_count = reader.read(1)
        else:
            reader.step(-1)

        reader.read_until("-")
        reader.step(1)

        self.size_GB = reader.read(2)
    
    def __proc_ADATA(self, model_code : str):
        reader = ModelReader(model_code)

        brand = reader.read(2)
        self.DDR = f"DDR{reader.read(1)}"
        type = reader.read(1)
        self.megaherz_base = reader.read_until_any("ABCDEF", 6)#not complete but going G or numerics could easily break this. Their part number system is easily L-R parsable
        reader.step(1)
        self.size_GB = reader.read_until_any("MG")
        if len(self.size_GB) > 2:
            self.size_GB = self.size_GB[-2:]
    
    def __proc_CORSAIR(self, model_code : str):
        reader = ModelReader(model_code)

        reader.step(2)
        kitline = reader.read(1)
        
        self.size_GB = reader.read_until('G')
        reader.step(2)
        
        self.DDR = f"DDR{reader.read(1)}"
        reader.step(1)
        kits = reader.read(1)
        version = reader.read(1)
        
        self.megaherz_base = reader.read_until_any("CZ")

    def foo(self, model_code : str):
        """noop used by dynamic dyspatch in process_modelcode for vendors with no documentation on their part numbers"""
        pass

    def process_modelcode(self):
        vendor_procs : dict[str, function[str, None]]= {
            "Team Group"    : self.__proc_teamgroup,
            "T-FORCE"       : self.__proc_teamgroup,
            "TEAMGROUP"     : self.__proc_teamgroup,
            "Kingston"      : self.__proc_kingston,
            "ADATA"         : self.__proc_ADATA,
            "ADATA(XPG)"    : self.__proc_ADATA,
            "CORSAIR"       : self.__proc_CORSAIR
        }
        vendor_procs.get(self.vendor, self.foo)(self.model)

    def __str__(self):
        return f"{self.vendor} {self.model} {self.megaherz_base}MHz {self.size_GB}GB {self.chipset} {self.DDR}"

#pain
def rcontains(a,b):
    return operator.contains(b, a)

class FilterEntry:
    comparator : Callable = operator.gt 
    value : Any = 0
    __op_lookup : dict = {
        "==" : operator.eq,
        "!=" : operator.ne,
        "in" : rcontains,
        ">" : operator.gt,
        "<" : operator.lt,
        ">=" : operator.ge,
        "<=" : operator.le
    }

    def __init__(self, comparator : Callable | str, value : Any):
        self.value = value

        if isinstance(comparator, str):
            assert comparator in self.__op_lookup, f"Invalid comparator string {comparator}!"
            comparator = self.__op_lookup[comparator]

        self.comparator = comparator
    
    def __call__(self, operand : Any) -> bool:
        print(self.comparator, operand, self.value)
        if type(self.value) in [int, float]:
            return self.comparator(int(operand), self.value)
        return self.comparator(operand, self.value)

def apply_filters(stick : RamInfo, filters : dict[str, FilterEntry]) -> bool:
    """
    Little easy function for checking whether a RamInfo matches a set of filters
    """
    for property, filter in filters.items():
        if not filter(stick.__getattribute__(property)):
            return False
    
    return True

def match_sticks(infos : list[RamInfo], filters : dict[str, FilterEntry]) -> list[RamInfo]:
    """
    Filters the list of ram stick infos
    """
    result : list[RamInfo] = []

    for stick in infos:
        if apply_filters(stick, filters):
            result.append(stick)

    return result
