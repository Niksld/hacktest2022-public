import dearpygui.dearpygui as dpg

from windows.Window import Window
from configuration import window_bg_color, networkmap_sizes

class WindowNetworkMap(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs)
        self.devices = []

        self.terminal_echo = None
        
        self.level4files = set()
        
    def setup(self):
        #  Vytvoření texture_tagu
        with dpg.texture_registry():
            for device in self.devices:
                imagedata = dpg.load_image(device.icon) #0: width, 1: height, 2: channels, 3: data
                dpg.add_static_texture(imagedata[0], imagedata[1], imagedata[3], tag=f"nm.icon-{device.name}")
        #  Vytvoří image_button pro každé přidané zařízení 
        for i in range(len(self.devices)):
            dpg.add_image_button(f"nm.icon-{self.devices[i].name}", tag=f"nm.button-{self.devices[i].name}", label=self.devices[i].name, width=networkmap_sizes["dev_size"], height=networkmap_sizes["dev_size"],
                background_color=window_bg_color, pos=(networkmap_sizes[f"dev{i}_posx"],networkmap_sizes[f"dev{i}_posy"]), user_data=(self.devices[i], i))
            dpg.hide_item(f"nm.button-{self.devices[i].name}")
    
    def set_devices(self, devices: list):
        self.devices = devices
    
    def set_terminal_echo(self, func: "function"):
        self.terminal_echo = func
    
    def load_level(self, leveldata: dict, level: int, quest: int):
        super().load_level(leveldata, level, quest)
        available_devices = leveldata["available_devices"]
        if "available_devices" in leveldata["quests"][quest]["extra"].keys():
            available_devices += leveldata["quests"][quest]["extra"]["available_devices"]
            available_devices = list(set(available_devices))
        for i in range(len(self.devices)):
            if i in available_devices:
                dpg.show_item(f"nm.button-{self.devices[i].name}")
        if dpg.does_item_exist("w.login"):
            self.force_connect(0)
    
    def update_filesystem(self, sender="", app_data=None, user_data=None):
        #userdata: fullpath, device index, download/remove
        sender = sender + "   "
        fs = self.devices[user_data[1]].filesystem
        path_list = user_data[0].strip("/").split("/")
        dirpath = "/" + ("/".join(path_list[:-1])) if len(path_list) > 1 else "(root)"
        match user_data[2]:
            case "download":
                decomposed_fs = [fs["content"]]
                for directory in path_list[:-1]:
                    decomposed_fs.append(decomposed_fs[-1][directory]["content"])
                self.devices[0].filesystem["content"]["download"]["content"][path_list[-1]] = decomposed_fs[-1][path_list[-1]].copy()
                if sender[0:3] == "fe.":
                    dpg.configure_item(f"fe.filemodal.{user_data[0]}", no_close=True)
                    dpg.configure_item(f"fe.filemodal.downloadbtn.{user_data[0]}", label="Stahování...")
                    self.terminal_echo(f"Stahování souboru {path_list[-1]} z adresáře {dirpath}")
                    
                #progress level 2-1 -> level 3-0
                if self.level == 2 and self.quest == 1 and user_data[0].strip("/") == "hacking-tools/sshcrack.exe" and user_data[1] == 1:
                    self.progress(3, 0)
                
                #progress level 4-2 -> level 5-0
                elif self.level == 4 and self.quest == 2 and user_data[1] == 3 and (user_data[0].strip("/") == "download/Nova_slozka(1)/hax-mobile/TunnelExpl0it.exe" or user_data[0].strip("/") == "download/Nova_slozka(1)/hax-mobile/mobile-gesture-hack.exe"):
                    self.level4files.add(user_data[0].strip("/"))
                    if len(self.level4files) == 2:
                        self.progress(5, 0)
                
                #progress level 5-3 -> level 6-0
                elif self.level == 5 and self.quest == 3 and user_data[0].strip("/") == r"download/download_727u%iwysiXhjpuQ_oi(1).jpeg" and user_data[1] == 4:
                    self.progress(6, 0)

            case "remove":
                decomposed_fs = [fs["content"]]
                for directory in path_list[:-1]:
                    decomposed_fs.append(decomposed_fs[-1][directory]["content"])
                del decomposed_fs[-1][path_list[-1]]
                self.devices[user_data[1]].filesystem["content"] = decomposed_fs[0]
                if sender[0:3] == "fe.":
                    dpg.configure_item(f"fe.filemodal.{user_data[0]}", no_close=True)
                    dpg.configure_item(f"fe.filemodal.removebtn.{user_data[0]}", label="Odstraňování...")
                    self.terminal_echo(f"Odstraňování souboru {path_list[-1]} z adresáře {dirpath}")
                
                #progress level 1-0 -> level 2-0
                if self.level == 1 and self.quest == 0 and user_data[0].strip("/") == "network/firewall/configuration.cfg" and user_data[1] == 0:
                    self.progress(2, 0)
        
        self.delay(3000)
        self.force_connect(user_data[1])
    
    def force_connect(self, index: int = 0):
        func = dpg.get_item_callback(f"nm.button-{self.devices[index].name}")
        user_data = dpg.get_item_user_data(f"nm.button-{self.devices[index].name}")
        func("w.networkmap", None, user_data)
