import dearpygui.dearpygui as dpg
from configuration import window_bg_color, dimensions, relpath, RELEASE_VERSION
from savegame import userfile_load, userfile_progress
from Timer import Timer

from json import load as jsonload
from threading import Thread

class GUI:
    def __init__(self):
        self.level = 0
        self.quest = 0
        self.windows = {}
        self.local_check_running = False

        dpg.create_context()
        
        #interval kontroly změny save souboru v render loopu
        self.local_timer = Timer(10) #ve skutečné hře musí být 10, jinak to uškvaří disk

        #theme a font oken
        with dpg.font_registry():
            with dpg.font(relpath("resources/fonts/UbuntuMono-R.ttf"), 15) as font1:
                dpg.add_font_range(0x0100, 0x017F)
            dpg.bind_font(font1)
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, window_bg_color, category=dpg.mvThemeCat_Core) #záhlaví
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20,20,20), category=dpg.mvThemeCat_Core) #pozadí (ass)
        dpg.bind_theme(global_theme)
        
        #viewport, ve kterém se zobrazují okna
        dpg.create_viewport(
            title=f"Hacktest {RELEASE_VERSION}",
            width=dimensions["v_width"],
            height=dimensions["v_height"],
            max_width=dimensions["v_width"],
            max_height=dimensions["v_height"],
            resizable=False,
            small_icon=relpath("resources/images/hacker.ico"),
            large_icon=relpath("resources/images/hacker.ico"))
        
    #přidá okno do seznamu oken, je to slovník ať si nemusíme pamatovat indexy
    def add_window(self, name: str, window):
        self.windows[name] = window
    
    def remove_window(self, name):
        del self.windows[name]
    
    #každé okno má svou setup metodu rozdílnou od initu, pro nastavení samostatných oken se musí zasahovat přímo do slovníku
    def setup_window(self, key: str = None): #levelfile
        if key is None:
            for w in self.windows.values():
                with w.window:
                    w.setup()
        else:
            with self.windows[key].window:
                self.windows[key].setup()
    
    #nepěkný ale funkční způsob, jak nastavit login oknu černé okolí
    def set_modal_theme(self, tag: str):
        if dpg.does_alias_exist(tag):
            with dpg.theme() as item_theme:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (0,0,0), category=dpg.mvThemeCat_Core)
            dpg.bind_item_theme(tag, item_theme)
    
    def progress(self, level, quest):
        print(F"PROGRESS TO {level}-{quest}")
        userfile_progress(level, quest)
        self.check_level_progress()
    
    #kontrola změny save souboru, při změně volá self.load_level
    def check_level_progress(self, depth=0):
        print("Local level check...")
        if not self.local_check_running:
            self.local_check_running = True
        else:
            print("\tLocal level check cancelled (currently running in another thread)")
            return
        try:
            userfile = userfile_load()
        except Exception: #pokud save soubor neexistuje (před prvním příhlášením) tak to pokaždé háže error
            self.local_check_running = False
            return
        
        try:
            file_level = userfile["level"]
            file_quest = userfile["quest"]
            
            print(f"\tBefore check: Session: {self.level}-{self.quest}, Local: {file_level}-{file_quest}")
            
            #level v souboru je vyšší, než ve hře (nastal pokrok levelu) => nastavit level ze souboru a quest na 0, propagovat změny do hry
            if self.level < file_level:
                self.level = file_level
                self.quest = file_quest
                self.load_level()
                
            #nemělo by se stát, hra má vyšší level než soubor, zapíše se do souboru a hra pokračuje beze změny
            elif self.level > file_level:
                print(f"\tWARN: Session level is {self.level} (quest {self.quest}) while file level is {file_level} (quest {file_quest}), updating file to session level")
                userfile_progress(self.level, self.quest)
            
            #quest v souboru je vyšší, než ve hře (nastal pokrok questu) => nastavit quest ze souboru, propagovat změny do hry
            elif self.quest < file_quest:
                self.quest = file_quest
                self.load_level()
            
            #nemělo by se stát, hra má vyšší quest než soubor, zapíše se do souboru a hra pokračuje beze změny
            elif self.quest > file_quest:
                print(f"\tWARN: Session level matches with file but quest is {self.quest} while file quest is {file_quest}, updating file")
                userfile_progress(self.level, self.quest)
            
            userfile = userfile_load()
            file_level = userfile["level"]
            file_quest = userfile["quest"]
            print(f"\tAfter check: Session: {self.level}-{self.quest}, Local: {file_level}-{file_quest}")
            if ((self.level != file_level) or (self.quest != file_quest)) and depth == 0:
                self.check_level_progress(depth=1)
        
        except Exception as e: #nikdy by nemělo nastat, chyba jinde než při načítání neexistujícího save souboru
            try:
                dpg.delete_item("w.login", children_only=True)
                dpg.add_text(f"Pokud toto vidíte, něco je špatně.\n{e}", parent="w.login", tag="l.hint", color=(255,0,0), wrap=dpg.get_item_configuration("w.login")["width"]-20)
            except Exception:
                with dpg.window(modal=True, no_resize=True, no_collapse=True, no_close=True, tag="w.fatalerror"):
                    dpg.add_text(f"Pokud toto vidíte, něco je špatně.\n{e}", color=(255,0,0), wrap=500)

        self.local_check_running = False
        
    
    #při změně levelu na X načte soubor levelX.json a odešle informace v něm všem oknům
    #ta okna, která musí něco dělat, mají předefinovanou load_level metodu, jinak to prostě jen načtou a uloží (dědí z třídy Window)  
    def load_level(self):
        print(f"\tLoading level {self.level} quest {self.quest}") #debug
        
        while True:
            try:
                with open(relpath(f"resources/levels/level{self.level}.json"), mode="r", encoding="utf-8") as levelfile:
                    leveldata = jsonload(levelfile)
                break
            except FileNotFoundError as e:
                print(f"\tWARN: Save file corruption (non-existent level), attempting restoration ({e})")
                if self.level < 1:
                    self.level = 1
                    self.quest = 0
                    userfile_progress(1, 0)
                    print("Restored progress to 1-0")
                elif self.level > 7:
                    self.level = 7
                    self.quest = 0
                    userfile_progress(7, 0)
                    print("Restored progress to 7-0")
                    
        valid_quests = range((len(leveldata["quests"])))
        if self.quest not in valid_quests:
            print(f"\tWARN: Save file corruption (non-existent quest), attempting restoration (Quest in save file: {self.quest}; Maximum allowed quest: {valid_quests[-1]})")
            self.quest = valid_quests[-1]
            userfile_progress(self.level, valid_quests[-1])
                
        for window in self.windows.values():
            window.load_level(leveldata, self.level, self.quest)
    
    #toto musí být ta ÚPLNĚ POSLEDNÍ metoda, která se v celém programu spustí
    def event_loop(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.check_level_progress()
        
        while dpg.is_dearpygui_running():
            if self.local_timer.update():
                local_thread = Thread(target=self.check_level_progress)
                local_thread.start()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()
