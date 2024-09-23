import dearpygui.dearpygui as dpg

from windows.Window import Window

class WindowNuclearCode(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs, horizontal_scrollbar=False)
        self.width = width-30
        self.correct_order = [6,9,1,3,3,7]
    
    def load_level(self, leveldata: dict, level: int, quest: int):
        super().load_level(leveldata, level, quest)
        if self.level == 6:
            # dpg.configure_item("w.nuclear", modal=True)
            dpg.show_item("w.nuclear")
    
    def submit(self, sender, app_data, user_data):
        order = []
        for i in range(6):
            order.append(dpg.get_value(f"c.input{i}"))
        for i in range(16):
            dpg.configure_item("c.submitbtn", label="ODESÍLÁNÍ" + i*".")
            self.delay(350)
        if order == self.correct_order:
            # dpg.configure_item("w.nuclear", modal=False)
            dpg.hide_item("w.nuclear")
            self.progress(7, 0)
        else:
            dpg.set_value("c.submittext", "Hmmm, toto mi nějak nesedí. Zkontrolujte ten kód, prosím.")
            dpg.configure_item("c.submitbtn", label="ODESLAT")
    
    def setup(self):
        dpg.add_text("Zdravím, jsem tajemník BSI. Opravdu vynikající práce, najmout si Vás nebyla chyba.\n\n\nPro ověření potřebuji opsat kód z fotky v jeho telefonu.", wrap=self.width)
        with dpg.group(tag="c.inputgroup"):
            for i in range(6):
                dpg.add_input_int(tag=f"c.input{i}", width=100, step=1, min_value=0, max_value=9, min_clamped=True, max_clamped=True)
                #dpg.add_combo(items=("0","1","2","3","4","5","6","7","8","9"), tag=f"c.dropdown{i}")
        with dpg.group(tag="c.submitgroup"):
            dpg.add_button(label="ODESLAT", height=60, tag="c.submitbtn", callback=self.submit)
            dpg.add_text(tag="c.submittext", color=(255,0,0))
            
