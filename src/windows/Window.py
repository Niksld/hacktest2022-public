import dearpygui.dearpygui as dpg

class Window:
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        self.window = dpg.window(
            width=width, 
            height=height,
            pos=pos,
            tag=tag,
            **kwargs,
            )
        self.level = 0
        self.progress = None
    
    def setup(self):
        dpg.add_text("Hello World!")
    
    #https://dearpygui.readthedocs.io/en/latest/documentation/staging.html?highlight=callback#wrapping-items-with-classes
    def set_callback(self, tag, callback):
        dpg.set_item_callback(tag, callback)
    
    def set_progress_function(self, func: "function"):
        self.progress = func
    
    def delay(self, delay: int = 0, mode: int = 0):
        '''mode 0: disable, delay, reenable; mode 1: disable, delay; mode 2: delay, enable'''
        button_ids = []
        for item in dpg.get_all_items():
            type = dpg.get_item_type(item)
            if type == "mvAppItemType::mvButton" or type == "mvAppItemType::mvImageButton":
                try:
                    if "fe.filemodal.removebtn." not in dpg.get_item_alias(item):
                        button_ids.append(item)
                except Exception:
                    button_ids.append(item)
                
        
        if mode != 2:
            for item in button_ids:
                try:
                    dpg.disable_item(item)
                except Exception:
                    print(f"Couldn't disable button {item}")
            
        dpg.split_frame(delay=delay)
        
        if mode != 1:
            for item in button_ids:
                try:
                    dpg.enable_item(item)
                except Exception:
                    print(f"Couldn't re-enable button {item}")
        
        
    
    # načítá informace o levelu, u oken co mají něco dělat se ta metoda musí předefinovat
    def load_level(self, leveldata: dict, level: int, quest: int):
        self.leveldata = leveldata
        self.level = level
        self.quest = quest
