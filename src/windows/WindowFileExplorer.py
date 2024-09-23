import dearpygui.dearpygui as dpg

from windows.Window import Window
from configuration import relpath

class WindowFileExplorer(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs)
        self.fs = None
        self.device_index = 0
        self.modal_tags = []
        self.modal_btn_tags = []
        self.image_names = []
        
        self.nm_callback = None
    
    def setup(self):
        dpg.add_text("Vyberte prosím zařízení z mapy sítě.", tag="fe.header")
        dpg.add_group(label="Soubory", tag="fe.files.") # TODO: tak nějak nefunguje odsazování hlubších složek, takže ty grupy jsou k ničemu

        with dpg.texture_registry():
            for image in self.image_names:
                imagedata = dpg.load_image(relpath(f"resources/images/{image}")) # 0: width, 1: height, 2: channels, 3: data
                dpg.add_static_texture(imagedata[0], imagedata[1], imagedata[3], tag=f"fe.image.{image}")
    
    def set_nm_callback(self, func: "function"):
        self.nm_callback = func
    
    def set_image_names(self, *args: str):
        for image in args:
            self.image_names.append(image)
    
    # toto volá network map. user_data obsahuje veškerá data o zařízení
    # sender a app_data tam musí být, i když to není potřeba, jinak to nefunguje
    def filesystem_load(self, sender=None, app_data=None, user_data=None):
        dpg.delete_item("fe.files.", children_only=True)
        for item in self.modal_tags:
            dpg.delete_item(item)
        self.modal_tags, self.modal_btn_tags = [], []
        dpg.set_value("fe.header", user_data[0].name)
        self.fs = user_data[0].filesystem
        self.device_index = user_data[1]
        self.filesystem_directory()

    #zobrazování obsahu složky, spuštěno při kliknutí na složku
    def filesystem_directory(self, sender=None, app_data=None, user_data=""):
        path = user_data
        current_dir = self.fs["content"]
        if path != "":
            path_list = path.strip("/").split("/")
            for directory in path_list:
                current_dir = current_dir[directory]["content"]
        
        for thing in current_dir:
            if not dpg.does_alias_exist(f"fe.filebtn.{path}/{thing}"):
                if current_dir[thing]["type"] != "dir":
                    dpg.add_button(label=f"{path}/{thing}", parent=f"fe.files.{path}", tag=f"fe.filebtn.{path}/{thing}", callback=self.filesystem_interaction, user_data=(current_dir[thing], f"{path}/{current_dir[thing]['name']}"), height=25)
                    self.modal_tags.append(f"fe.filemodal.{path}/{thing}")
                    #context menu při kliknutím pravým na tlačítko souboru
                    with dpg.popup(parent=f"fe.filebtn.{path}/{thing}", mousebutton=dpg.mvMouseButton_Right, modal=True, tag=f"fe.filemodal.{path}/{thing}"):
                        # dpg.add_button(label="Fix", tag=f"fe.filemodal.fixbtn.{current_dir[thing]['name']}")
                        #pokud je soubor stažitelný/smazatelný, objeví se tlačítko, jinak text (určuje se v json)
                        #při stažení souboru se soubor umístí do (případně přepíše v) localhost/download/
                        #při odstranění souboru se odstraní ve hře, ale ne v json
                        #problém: po zavření hry se změny vůbec neuloží
                        
                        dpg.add_button(label="Stáhnout", tag=f"fe.filemodal.downloadbtn.{path}/{thing}", user_data=(f"{path}/{thing}", self.device_index, "download"), callback=self.nm_callback)
                        self.modal_btn_tags.append(f"fe.filemodal.downloadbtn.{path}/{thing}")
                        if not current_dir[thing]['downloadable']:
                            dpg.disable_item(f"fe.filemodal.downloadbtn.{path}/{thing}")
                            dpg.configure_item(f"fe.filemodal.downloadbtn.{path}/{thing}", label="Nelze stáhnout")

                        dpg.add_button(label="Odstranit", tag=f"fe.filemodal.removebtn.{path}/{thing}", user_data=(f"{path}/{thing}", self.device_index, "remove"), callback=self.nm_callback)
                        self.modal_btn_tags.append(f"fe.filemodal.removebtn.{path}/{thing}")
                        if not current_dir[thing]['removable']:
                            dpg.disable_item(f"fe.filemodal.removebtn.{path}/{thing}")
                            dpg.configure_item(f"fe.filemodal.removebtn.{path}/{thing}", label="Nelze odstranit")
                        
                        dpg.add_button(label="Zkopírovat název", tag=f"fe.filemodal.copynamebtn.{path}/{thing}", user_data=(path, thing), callback=lambda s,a,u: (dpg.set_clipboard_text(u[1]), dpg.hide_item(f"fe.filemodal.{u[0]}/{u[1]}")))
                        dpg.add_button(label="Zkopírovat cestu", tag=f"fe.filemodal.copypathbtn.{path}/{thing}", user_data=(path, thing), callback=lambda s,a,u: (dpg.set_clipboard_text(u[0]), dpg.hide_item(f"fe.filemodal.{u[0]}/{u[1]}")))

                    dpg.configure_item(f"fe.filemodal.{path}/{thing}", label=thing)
                    dpg.configure_item(f"fe.filemodal.{path}/{thing}", pos=(100,100))
                        
                else:
                    dpg.add_group(tag=f"fe.files.{path}/{thing}", parent=f"fe.files.{path}")
                    dpg.add_button(label=f"{path}/{thing}", parent=f"fe.files.{path}/{thing}", tag=f"fe.filebtn.{path}/{thing}", callback=self.filesystem_directory, user_data=f"{path}/{current_dir[thing]['name']}", height=40)
    
    #spuštěno při kliknutí na něco, co není složka
    def filesystem_interaction(self, sender=None, app_data=None, user_data=None):
        with dpg.window(label=user_data[0]["name"], tag=user_data[1], modal=True, pos=(50,50), min_size=(350,200), max_size=(700,500), horizontal_scrollbar=True, no_resize=True, on_close=lambda: dpg.delete_item(user_data[1])):
            match user_data[0]["type"]:
                case "text":
                    dpg.add_text(user_data[0]["content"])
                
                case "audio":
                    dpg.add_text("Nepodařilo se přehrát zvukový soubor.\nPokud se tato chyba opakuje, kontaktujte administrátora.", wrap=480)
                
                case "exe":
                    dpg.add_text("Spuštění programu selhalo (chybějící parametry, zkuste program spustit jako příkaz v terminálu).", wrap=480)

                case "apk":
                    dpg.add_text("Nepodporovaný formát aplikačního balíčku na platformě uOS.")

                case "image":
                    dpg.add_image(f"fe.image.{user_data[0]['content']}")

                case _:
                    dpg.add_text("Nepodporovaný soubor.\nKontaktujte administrátora pro pomoc.")

