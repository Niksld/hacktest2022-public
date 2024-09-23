import dearpygui.dearpygui as dpg

from windows.Window import Window
from savegame import userfile_check, userfile_overwrite

class WindowLogin(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs)
        self.width = width-20
        self.local_status = -1 # 1: soubor existuje, 0: soubor neexistuje, -1 a -2: problem
        self.gui_gui_level_progress = None
    
    def setup(self):
        self.local_status = userfile_check()
        match self.local_status:
            case 1: #soubor existuje a ma platne udaje
                dpg.add_text(f"Obnovování uložené hry...", wrap=self.width)
            case 0:
                dpg.add_text("Vítejte v Hacktestu.", tag="l.hint", wrap=self.width)
                dpg.add_button(tag="l.login_button", label="Nová hra", height=50, callback=self.login)
            case -2:
                dpg.add_text("Nepodařilo se obnovit relaci, uložená data jsou poškozená.", tag="l.hint", color=(255,0,0), wrap=self.width)
                dpg.add_button(tag="l.login_button", label="Nová hra", height=50, callback=self.login)
    
    def login(self, sender=None, app_data=None, user_data=None):
        userfile_overwrite({"level": 1, "quest": 0})
        dpg.delete_item("w.login", children_only=True)
        dpg.add_text(f"Zahajování hry...", wrap=self.width-20, parent="w.login")
        print("Logging in...")
        self.gui_gui_level_progress()
    
    def set_gui_level_progress(self, func: "function"):
        self.gui_gui_level_progress = func
    
    def load_level(self, leveldata: dict, level: int, quest: int):
        super().load_level(leveldata, level, quest)
        if self.local_status != -1:
            try:
                dpg.delete_item("w.login")
            except Exception:
                pass
