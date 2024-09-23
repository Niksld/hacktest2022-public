import dearpygui.dearpygui as dpg

from windows.Window import Window
from random import choice, randint

class WindowTerminal(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs, horizontal_scrollbar=False)
        self.width = width-30
        self.height = height
        
        self.fs = None
        self.device_index = 0
        self.dir = ""

        self.device_refs = [] #seznam tuplů (ip, jméno)
        self.available_devices = []
        self.available_devices = []
        self.nm_button_press = None
        self.nm_callback = None
        self.h_callback = None

        self.log = (25*"\n") + "Příkaz 'help' vypíše seznam dostupných příkazů\n"
        self.common_commands = ["help", "echo", "cd", "ls", "rm", "remove", "dl", "download", "ipconfig", "debuglvl"]
        self.available_commands = []
        self.help_ignored = {"echo", "remove", "download", "network", "debuglvl"}
        self.help_commands = {
            "help": "help: seznam všech dostupných příkazů",
            "cd": "cd <cesta/k/adresáři>: změní adresář\ncd ..: změní adresář na nadřazený adresář",
            "ls": "ls: vypíše obsah aktuálního adresáře",
            "rm": "rm <soubor>: odstraní soubor",
            "dl": "dl <soubor>: stáhne (zkopíruje) soubor",
            "nw": "nw connect <IP adresa>: připojení k zařízení podle jeho IP adresy\nnw scan: vyhledání zařízení v sítí",
            "ipconfig": "ipconfig: vypíše IP adresu aktuálního zařízení",
            "sshcrack": "sshcrack <IP adresa>: nabourá se do zařízení podle IP adresy",
            "tunnelexploit": "tunnelexploit <URL VPN>: odhalí skutečnou IP adresu skrytou pod URL VPN",
            "gesturehack": "gesturehack <IP adresa> slouží k prolomení gesta mobilních zařízení",
            "debuglvl": ":)"
        }
        # Seznam IP adres, které SSHCrack a network connect odmítnou jako "přístup" (úlohy 4 a 5)
        self.refused_ips = ['176.36.95.56', '77.69.58.73', '77.69.58.73:6779', '69.56.35.5', '169.42.0.61',
               '108.177.13.106', '97.109.111.103', '202.81.9.15', '88.198.10.117',
               '147.229.242.34', '151.101.193.69', '23.15.68.13', '88.199.4.20', '168.64.69.42']
    
    def setup(self):
        dpg.add_text(self.log, tag="t.terminal", wrap=self.width, track_offset=10.0, tracked=True)
    
    def set_nm_callback(self, func: "function"):
        self.nm_callback = func

    def set_nm_button_press(self, func: "function"):
        self.nm_button_press = func
    
    def set_h_callback(self, func: "function"):
        self.h_callback = func

    def load_level(self, leveldata: dict, level: int, quest: int):
        super().load_level(leveldata, level, quest)
        self.available_commands = leveldata["available_commands"] + leveldata["quests"][quest]["available_commands"]
        self.available_devices = leveldata["available_devices"]
        if "available_devices" in leveldata["quests"][quest]["extra"].keys():
            self.available_devices += leveldata["quests"][quest]["extra"]["available_devices"]
            self.available_devices = list(set(self.available_devices))
    
    def filesystem_load(self, sender=None, app_data=None, user_data=None):
        self.fs = user_data[0].filesystem
        if user_data[1] != self.device_index:
            self.device_index = user_data[1]
            self.dir = ""
        dpg.configure_item("w.terminal", label=f"Terminal ({user_data[0].name}@{user_data[0].ip})")

    def set_devices(self, devices: tuple[str, str]):
        self.device_refs = devices
    
    def get_current_dir(self) -> tuple[dict, list]:
        current_path_list = self.dir.strip("/").split("/")
        current_dir = self.fs["content"]
        if current_path_list != [""] and current_path_list != []:
            for directory in current_path_list:
                current_dir = current_dir[directory]["content"]
        return current_dir

    #funkce pro příkazy spuštěné uživatelem
    def cmd_echo(self, args, no_newline=False):
        self.log += str(args)
        if not no_newline:
            self.log += "\n"
        dpg.set_value("t.terminal", self.log)

    def cmd_cd(self, args):
        if len(args) > 0:
            if args[0] != "..":
                current_dir = self.get_current_dir()
                
                path_list = args[0].strip("/").split("/")
                for directory in path_list:
                    if directory in current_dir.keys():
                        if current_dir[directory]["type"] == "dir":
                            current_dir = current_dir[directory]["content"]
                            self.dir += f"/{directory}"
                        else:
                            self.cmd_echo(f"Chyba: {directory} v adresáři {self.dir if self.dir != '' else '(root)'} je soubor")
                            break
                    else:
                        self.cmd_echo(f"Chyba: Adresář {directory} v adresáři {self.dir if self.dir != '' else '(root)'} nenalezen")
                        break
                else:
                    self.cmd_echo(f"Adresář změněn na {self.dir}")
            else:
                self.dir = "/".join(self.dir.strip("/").split("/")[:-1])
                self.cmd_echo(f"Adresář změněn na {self.dir if self.dir != '' else '(root)'}")

        else:
            self.cmd_echo("Chyba: Nebyl zadán žádný adresář. Správná syntaxe je: 'cd <adresář>' nebo 'cd ..'")
    
    def cmd_ls(self, args):
        current_dir = self.get_current_dir()
        self.cmd_echo(f"Obsah adresáře {self.dir if self.dir != '' else '(root)'}:")
        self.cmd_echo(", ".join([thing for thing in current_dir.keys()]))

    def cmd_dl_rm(self, args, mode: str = "download"):
        match mode:
            case "download":
                words = ["Stahování", "stáhnout", "downloadable", "dl"]
            case "remove":
                words = ["Odstraňování", "odstranit", "removable", "rm"]
            case _:
                return

        if len(args) > 0:
            filename = args[0].strip("/")
            current_dir = self.get_current_dir()
            if filename in current_dir.keys():
                if current_dir[filename]["type"] != "dir":
                    if current_dir[filename][words[2]]:
                        self.cmd_echo(f"{words[0]} souboru {filename} z adresáře {self.dir if self.dir != '' else '(root)'}")
                        self.nm_callback("w.terminal", None, (f"{self.dir}/{filename}", self.device_index, mode))
                    else:
                        self.cmd_echo(f"Soubor {filename} v adresáři {self.dir if self.dir != '' else '(root)'} nelze {words[1]}")
                else:
                    self.cmd_echo(f"Adresář {filename} v adresáři {self.dir if self.dir != '' else '(root)'} nelze {words[1]}")
            else:
                self.cmd_echo(f"Chyba: Adresář {self.dir if self.dir != '' else '(root)'} neobsahuje soubor {filename}")
        else:
            self.cmd_echo(f"Chyba: Nebyl zadán žádný soubor. Správná syntaxe je: '{words[3]} <soubor>' včetně přípony souboru")
    
    def cmd_ipconfig(self, args):
        self.cmd_echo(f"IP adresa zařízení je: {self.device_refs[self.device_index][0]}")

    def cmd_sshcrack(self, args):
        if dpg.is_item_shown("w.sshcrack"):
                self.cmd_echo("Chyba: Program SSHCrack již běží")
                dpg.focus_item("w.sshcrack")

        elif len(args) >= 1:
                match args[0], self.level, self.quest:
                    case ("103.101.45.120", 3, 0) | ("103.101.45.120", 3, 1):
                        dpg.show_item("w.sshcrack")
                        dpg.focus_item("w.sshcrack")

                    case "103.101.45.120", 3, 2:
                        self.cmd_echo("Chyba: Přístup k zařízení byl již navázán")
                        
                    case ("85.45.120.95", 4, 0) | ("85.45.120.95", 4, 1):
                        dpg.show_item("w.sshcrack",)
                        dpg.focus_item("w.sshcrack")
                    
                    case "85.45.120.95", 4, 2:
                        self.cmd_echo("Chyba: Přístup k zařízení byl již navázán")
                    
                    case ("103.101.45.120", _, _) | ("85.45.120.95", _, _):
                        self.cmd_echo("Chyba: Přístup k zařízení byl již navázán")
                        
                    case _:
                        if args[0] in self.refused_ips:
                            self.cmd_echo("Chyba: Přístup odepřen")        
                        else:
                            self.cmd_echo("Chyba: Neplatná IP adresa")
        else:
            self.cmd_echo("Chyba: Nebyla zadána IP adresa pro prolomení. Správná syntaxe je: 'sshcrack <IP adresa>'")
    
    def cmd_gesturehack(self, args):
        if dpg.is_item_shown("w.gesture"):
            self.cmd_echo("Chyba: Program GestureHack již běží")
            dpg.focus_item("w.gesture")
        
        elif len(args) >= 1:
            if args[0] == "65.42.240.120":
                if self.level == 5 and self.quest < 3:
                    dpg.show_item("w.gesture")
                    dpg.focus_item("w.gesture")
                else:
                    self.cmd_echo("Chyba: Gesto k tomuto zařízení bylo již prolomeno")
            else:
                self.cmd_echo(f"Chyba: Připojení k {args[0]} selhalo")
        else:
           self.cmd_echo("Chyba: Nebyla zadána IP adresa pro prolomení. Správná syntaxe je: 'gesturehack <IP adresa>'")
        
            
                
    def cmd_tunnelexploit(self, args):
        # Klidne sem dejte slova, ale UPPER CASE/CAPS
        # Slova musi mit 6 pismen.
        passwords = ['POGGER','HACKED','POWERS','ROMANR','DLOADR','CRINGE','HELPME','PLEASE','AMOGUS','KDIUPR']
        if len(args) >= 1:
            if args[0] == "nerdvpn.secure.net":
                if (self.level, self.quest) == (5, 0) or (self.level, self.quest) == (5, 1):
                    self.delay(10, 1)
                    word, line = choice(passwords), []
                    
                    for i in range(6):
                        self.cmd_echo(f"TUNN3L3XPL0IT - Pass {i+1}\n"+20*'-')
                        
                        # Generovani 6 lajn nahodnych pismenek + pismenka z hesla
                        for l in range(6):
                            dpg.split_frame(delay=500)
                            temp, line = "",[]
                            # Generovani stringu nul
                            for j in range(20):
                                line.append(0)
                                
                            # nahazeni random pismenek 
                            if i != 5:
                                for k in range(int(20/int(i+1))):
                                    line[randint(0,19)] = choice('abcdefghijklmnopqrstuvwxyz123456789')
                            line[randint(0,19)] = word[l]
                            
                            for n in range(20):
                                temp += f'{line[n]} '
                            self.cmd_echo(temp)
                        self.cmd_echo(20*'-'+'\n')
                        dpg.split_frame(delay=350)
                        
                    dpg.split_frame(delay=1000)
                    self.cmd_echo("Rozšifrovávání", no_newline=True)
                    for i in range(50):
                        self.cmd_echo(".", no_newline=True)
                        dpg.split_frame(delay=100)
                    self.cmd_echo("\nDokončeno!\n\nRozšifrované zařízení z adresy nerdvpn.secure.net:\n\tRoman`s uPhone@65.42.240.120")
                    self.delay(10, 2)
                    self.progress(5, 2)
                    
                elif (self.level == 5 and self.quest > 1) or self.level > 5:
                    self.cmd_echo("Rozšifrované zařízení z adresy nerdvpn.secure.net:\n\tRoman`s uPhone@65.42.240.120")
                
                else:
                    self.cmd_echo("Chyba: Kritická chyba programu (0x005005506804)") #nemělo by se nikdy stát, level nižší než 5
            else:
                self.cmd_echo(f"Chyba: Připojení k {args[0]} selhalo")
        else:
            self.cmd_echo("Chyba: Nebylo zadáno URL VPN k prolomení. Správná syntaxe je 'tunnelhack <URL VPN>'")
                
    def cmd_network(self, args):
        if len(args) > 0:
            match args[0]:
                case "connect":
                    self.delay(300)
                    if len(args) >= 2:
                        if "localhost" == args[1]:
                            self.cmd_echo(f"Připojeno k localhost")
                            self.device_index = 0
                            self.nm_button_press(0)
                        else:
                            for i in self.available_devices:
                                if self.device_refs[i][0] == args[1]:
                                    self.cmd_echo(f"Připojeno k {args[1]}")
                                    self.device_index = i
                                    self.nm_button_press(i)
                                    break
                            else:
                                if args[1] in self.refused_ips or (args[1] == "85.45.120.95" and self.level == 4 and self.quest == 1) or (args[1] == "65.42.240.120" and self.level == 5 and self.quest < 3):
                                    self.cmd_echo("Chyba: Přístup odepřen")
                                else:
                                    self.cmd_echo("Chyba: Neplatná IP adresa")
                    else:
                        self.cmd_echo("Chyba: Nebyla zadána IP adresa. Správná syntaxe je: 'nw connect <IP adresa>'")
            
                case "scan":
                    for i in range(16):
                        dpg.configure_item("w.networkmap", label=f"Network map (prohledávání sítě{((i%4))*'.'})")
                        self.delay(150)
                    match self.level, self.quest:
                        case 2, 0:
                            self.progress(2, 1)
                            self.cmd_echo(f"Nalezená zařízení (1):\n\t{self.device_refs[1][1]}@{self.device_refs[1][0]}\nDostupná zařízení automaticky aktualizována")
                        
                        case (3, 0) | (3, 1):
                            self.progress(3, 1)
                            self.cmd_echo(f"Nalezená zařízení (1):\n\t{self.device_refs[2][1]}@{self.device_refs[2][0]}\n\tNastala chyba při automatické aktualizaci dostupných zařízení")
                            
                        case (4, 0) | (4, 1):
                            self.progress(4, 1)
                            self.cmd_echo(f"""Nalezená zařízení (14):
Online (12):                            
\tPablo-listener@77.69.58.73:6779
\tLesterCrest@69.56.35.5
\tLenOwO@169.42.0.61
\tondrejtra@108.177.13.106
\taSUS@97.109.111.103
\tPC-V-KUCHYNI@202.81.9.15
\tmichaelcze@88.198.10.117
\tbarca445@147.229.242.34
\t{self.device_refs[3][1]}@{self.device_refs[3][0]}
\tniksld@151.101.193.69
\tbsi-dodavka215@88.199.4.20
\tLeoPC@168.64.69.42
Timed out (2):
\tZEUS@176.36.95.56 (timeout)
\tUbiServer3@23.15.68.13 (timeout)
Dostupná zařízení nebyla automaticky aktualizována
""")
                            
                        case (5, 0) | (5, 1):
                            self.progress(5, 1)
                            self.cmd_echo("""Nalezená zařízení (205):
Online (2):
\tTestServer@103.101.45.120
\t(neznámé jméno)@nerdvpn.secure.net

Timed out (203):
\tTestServer2@204.125.31.48 (timeout)
\tbsi-dodavka215@176.36.95.56 (timeout)
\tUbiServer3@23.15.68.13 (timeout)

Seznam 200 dalších zařízení skryt...
Dostupná zařízení nebyla automaticky aktualizována
""")
                        
                        case _:
                            self.cmd_echo("Nebyla nalezena žádná nová zařízení")

                    dpg.configure_item("w.networkmap", label="Network map")
                    
                case _:
                    self.cmd_echo(f"Chyba: Neplatný podpříkaz, platné podpříkazy jsou 'nw scan' a 'nw connect'")
        else:
            self.cmd_echo(f"Chyba: Nebyl zadán žádný podpříkaz, platné podpříkazy jsou 'nw scan' a 'nw connect'")
            
            
    def run(self, sender = None, callback = None):
        #skrytí historie, pokud je vidět
        if dpg.is_item_shown("w.history"):
            dpg.hide_item("w.history")
        #zapsání do historie
        self.h_callback(str(callback))
        #log uživatelského vstupu
        self.log += f"\nroot@{'localhost' if self.device_index == 0 else str(self.device_refs[self.device_index][0])}:{self.dir} $ {str(callback)}\n"
        dpg.set_value("t.terminal", self.log)
        #vymazání obsahu inputu
        dpg.set_value("i.input", "")
        dpg.focus_item("i.input")
        self.delay(70)
        command = str(callback).split()
        if len(command) == 0:
            self.cmd_echo("Chyba: Nebyl zadán žádný příkaz, zadej 'help' pro seznam příkazů")
        if command[0] in self.available_commands + self.common_commands:

            match command:
                case "debuglvl", *args:
                    # if len(args) == 2:
                    #     if args[0].isdigit() and args[1].isdigit():
                    #         self.progress(int(args[0]), int(args[1]))
                    #         self.cmd_echo(f"Level nastaven na {args[0]}-{args[1]}")
                    # else:
                    #     self.cmd_echo("Chyba, správná syntaxe je 'debuglvl <level> <quest>' (to bys měl vědět bruh)")
                    self.cmd_echo("Zaznamenáno neoprávněné zasahování do průběhu hry. Tento incident bude nahlášen.")
                        
                case "echo", *args:
                    self.cmd_echo(" ".join(args))
                
                case "cd", *args:
                    self.cmd_cd(args)
                
                case "ls", *args:
                    self.cmd_ls(args)
                
                case ("rm", *args) | ("remove", *args):
                    self.cmd_dl_rm(args, mode="remove")
                
                case ("dl", *args) | ("download", *args):
                    self.cmd_dl_rm(args, mode="download")
                
                case "ipconfig", *args:
                    self.cmd_ipconfig(args)
                
                case ("nw", *args) | ("network", *args):
                    self.cmd_network(args)

                case "sshcrack", *args:
                    self.cmd_sshcrack(args)
                
                case "tunnelexploit", *args:
                    self.cmd_tunnelexploit(args)
                
                case "gesturehack", *args:
                    self.cmd_gesturehack(args)
                
                case ["help", *_]:
                    self.cmd_echo("\n".join([self.help_commands[description] for description in set(self.common_commands + self.available_commands) - self.help_ignored]))
                
                case _:
                    self.cmd_echo("Chyba: Neplatný příkaz. Zadej 'help' pro seznam všech dostupných příkazů")
        else:
            self.cmd_echo("Chyba: Neznámý příkaz. Zadej 'help' pro seznam všech dostupných příkazů")
