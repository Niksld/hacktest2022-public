from json import load as jsonload

class Device:
    def __init__(self, name: str, ip: str, icon: str, filesystem: str):
        self.name = name
        self.ip = ip
        self.icon = icon
        with open(filesystem, mode="r", encoding="utf-8") as filesystem_file:
            self.filesystem = jsonload(filesystem_file)
    
    def __str__(self):
        return f"root@{self.name}"

# json formát:
# name: název souboru nebo složky
# type: určuje typ souboru/složky (složka: dir)
# content: pro složky je to slovník souborů (klíče jsou názvy souborů, hodnoty jsou opět slovníky s name/type/content a tak furt dokola), pro soubory záleží dle typu souboru
