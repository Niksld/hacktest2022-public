from random import choice
from os import path as ospath, sep as pathseparator
import sys
from platform import system

operating_system = system()

RELEASE_VERSION = "2022.1.0"

#určí relativní cestu, nezbytné pro pyinstaller
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = sys._MEIPASS
    # if ".exe" in application_path:
    #     application_path = "\\".join(application_path.split("\\")[:-1])
else:
    APPLICATION_PATH = ospath.dirname(ospath.abspath(__file__))

#funkce pro převedení relativní cesty na cestu pro pyinstaller
def relpath(path: str, application_path=APPLICATION_PATH) -> str:
    return application_path + pathseparator + path.replace("/", pathseparator)

#TAJNÝ klíč pro šifrování save souboru
FERNET_KEY = b'bTnf-SHI21dYPt7xoflIcaqRv-mN-thR-CeTVvkxg1o=' # Placeholder key - not used in prod. - 23/09/2024

#náhodně vybere barvu záhlaví oken
window_bg_color = choice([(102, 0, 0), (0, 153, 0)])

#vrací True pokud rozlišení < 1280x720
try:
    from ctypes import windll
    small_gui = windll.user32.GetSystemMetrics(0) < 1280 or windll.user32.GetSystemMetrics(1) < 720
except Exception:
    small_gui = False
if not small_gui:
    #rozměry při větším rozlišení - 1280x720 16:9
    dimensions = {
        "width": 640,
        "height": 400, 
        "fe_height": 500,
        "ssh_g_c_height": 500,
        "nm_height": 220,
        "q_height": 300,
        "t_height": 340,
        "i_height": 80,
        "l_height": 180,
        "l_width": 320,
        "v_width": 1280,
        "v_height": 720
    }

    networkmap_sizes = {
        "dev_size": 50,
        "dev0_posx": 50,
        "dev0_posy": 70,
        "dev1_posx": 120,
        "dev1_posy": 70,
        "dev2_posx": 310,
        "dev2_posy": 60,
        "dev3_posx": 500,
        "dev3_posy": 50,
        "dev4_posx": 530,
        "dev4_posy": 110
    }
    
    sshcrack_conf = {
        'x_pos_r1': 10,
        'x_pos_r2': 525,
        'y_pos': [30,180,330,30,180,330]
    }
    
    gesturehack_conf = {
        'btn': 50,
        'gap': 100,
        'x_offset': 50,
        'y_offset': 150
    }

else:
    #rozměry při menším rozlišení - 800x600 4:3
    dimensions = {
        "width": 400, 
        "height": 300,
        "fe_height": 400,
        "ssh_g_c_height": 600,
        "nm_height": 200,
        "q_height": 210,
        "t_height": 330,
        "i_height": 100,
        "l_height": 180,
        "l_width": 320,
        "v_width": 800,
        "v_height": 600
    }

    networkmap_sizes = {
        "dev_size": 40,
        "dev0_posx": 40,
        "dev0_posy": 60,
        "dev1_posx": 90,
        "dev1_posy": 60,
        "dev2_posx": 220,
        "dev2_posy": 50,
        "dev3_posx": 310,
        "dev3_posy": 40,
        "dev4_posx": 310,
        "dev4_posy": 100
    }
    
    sshcrack_conf = {
        'x_pos_r1':10,
        'x_pos_r2': 285,
        'y_pos': [30,150,270,30,150,270]
    }
    
    gesturehack_conf = {
        'btn': 40,
        'gap': 80,
        'x_offset': 30,
        'y_offset': 210
    }

#běžná nastavení pro každé okno
window_properties = {"no_resize": True, "no_move": True, "no_collapse": True, "no_close": True}
