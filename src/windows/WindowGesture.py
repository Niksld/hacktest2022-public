import dearpygui.dearpygui as dpg

from windows.Window import Window
from configuration import gesturehack_conf

class WindowGesture(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs, horizontal_scrollbar=False)
        self.width = width-30
        
        self.correct_order = [4,5,1,8,6,3]
        self.order = []
        self.linetags = []
        
    def setup(self):
        dpg.add_text("Klikej na očíslovaná tlačítka pro nakreslení gesta. Při úspěšné kombinaci se mezi nimi objeví zelená čára, při chybné zčervená. Pro začátek proklikávej všechna čísla v pořadí, dokud se neobjeví čára, to bude první číslo. Opakuj tak dlouho, dokud nezjistíš správnou kombinaci.", tag="g.guide", wrap=self.width)
        dpg.add_text(tag="g.order")
        for i in range(1,10):
            dpg.add_button(label=str(i), tag=f"g.button{i}", width=gesturehack_conf["btn"], height=gesturehack_conf["btn"], pos=(gesturehack_conf["x_offset"] + ((i-1)%3)*gesturehack_conf["gap"],gesturehack_conf["y_offset"] + ((i-1)//3)*gesturehack_conf["gap"]), user_data=i, callback=self.update)
    
    def update(self, sender, app_data, user_data):
        if user_data not in self.order:
            if len(self.order) == 0:
                dpg.set_value("g.order", "")
                for line in self.linetags:
                    dpg.delete_item(line)
                self.linetags = []
            self.order.append(user_data)
            dpg.configure_item("g.order", color=(255,255,255))
            dpg.set_value("g.order", " ".join(str(x) for x in self.order))
            
            if len(self.order) > 1:
                pos1 = dpg.get_item_pos(f"g.button{self.order[-2]}")
                pos1 = (pos1[0]+15, pos1[1]-5)
                pos2 = dpg.get_item_pos(f"g.button{self.order[-1]}")
                pos2 = (pos2[0]+15, pos2[1]-5)
                dpg.draw_line(pos1, pos2, thickness=10.0, color=(0,204,0,75), parent="w.gesture", tag=f"g.line.{self.order[-2]}-{self.order[-1]}")
                self.linetags.append(f"g.line.{self.order[-2]}-{self.order[-1]}")
            
            if self.order[-1] != self.correct_order[len(self.order)-1]:
                self.order = []
                dpg.configure_item("g.order", color=(255,0,0))
                for line in self.linetags:
                    dpg.configure_item(line, color=(204,0,0,75))
                
            elif len(self.order) == len(self.correct_order):
                dpg.configure_item("g.order", color=(0,255,0))
                dpg.add_button(label="PROLOMIT", tag="u.successbtn", parent="w.gesture", height=gesturehack_conf["btn"], pos=(gesturehack_conf["x_offset"],gesturehack_conf["y_offset"]+3*gesturehack_conf["gap"]+10) , callback=self.success)
                # for line in self.linetags:
                #     dpg.delete_item(line)
                # self.order = []
                # self.linetags = []
    
    def success(self, sender, app_data, user_data):
        for i in range(12):
            dpg.configure_item("u.successbtn", label="PROLAMOVÁNÍ" + i*".")
            self.delay(500)
        dpg.set_value("g.order", "")
        for line in self.linetags:
            dpg.delete_item(line)
        self.order = []
        self.linetags = []

        if self.level == 5 and self.quest < 3:
            self.progress(5, 3)
        
        dpg.hide_item("w.gesture")
