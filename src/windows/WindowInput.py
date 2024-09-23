import dearpygui.dearpygui as dpg

from windows.Window import Window

class WindowInput(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs, no_title_bar=True)
        self.width = width-30
    
    def setup(self):
        with dpg.group(horizontal=True, tag="i.group"):
            dpg.add_button(label="Historie", callback=self.open_history)
            dpg.add_input_text(width=self.width, on_enter=True, tag="i.input")
    
    def open_history(self, sender = None, app_data = None, user_data = None):
        if not dpg.is_item_shown("w.history"):
            dpg.configure_item("w.history", show=True)
            dpg.focus_item("w.history")
        else:
            dpg.configure_item("w.history", show=False)
            dpg.focus_item("i.input")
