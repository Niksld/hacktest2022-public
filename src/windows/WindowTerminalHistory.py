import dearpygui.dearpygui as dpg

from windows.Window import Window

class WindowTerminalHistory(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs, horizontal_scrollbar=False)
        self.run_history = []
    
    def setup(self):
        pass

    def update_run_history(self, command: str):
        self.run_history.insert(0, command)
        dpg.delete_item("w.history", children_only=True)
        for item in self.run_history:
            with dpg.group(parent="w.history", horizontal=True):
                dpg.add_button(label="Použít", user_data=item, callback=lambda s,a,u: (dpg.set_value("i.input", u), dpg.focus_item("i.input"), dpg.hide_item("w.history")))
                dpg.add_button(label="Zkopírovat", user_data=item, callback=lambda s,a,u: (dpg.set_clipboard_text(u), dpg.focus_item("i.input"), dpg.hide_item("w.history")))
                dpg.add_text(item)

