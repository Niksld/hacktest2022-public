import dearpygui.dearpygui as dpg

from windows.Window import Window

class WindowQuest(Window):
    def __init__(self, width: int, height: int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs)
        self.width = width

    def setup(self):
        dpg.add_progress_bar(label="Postup", tag="q.progress", default_value=0.0, overlay="Level N/A (N/A b)", width=200 if self.width < 640 else 300)
        dpg.add_text("Není načten žádný úkol.\nPokud toto vidíte, něco je špatně.", tag="q.quest_content", wrap=self.width-20)

    def load_level(self, leveldata: dict, level: int, quest: int):
        super().load_level(leveldata, level, quest)
        dpg.set_value("q.progress", leveldata['percentage']/100)
        dpg.configure_item("q.progress", overlay=f"{leveldata['name']} ({leveldata['points']} b)")
        dpg.set_value("q.quest_content", leveldata["quests"][quest]["content"])
