from GUI import GUI
from windows.WindowFileExplorer import WindowFileExplorer
from windows.WindowNetworkMap import WindowNetworkMap
from windows.WindowTerminal import WindowTerminal
from windows.WindowQuest import WindowQuest
from windows.WindowInput import WindowInput
from windows.WindowLogin import WindowLogin
from windows.WindowSSHCrack import WindowSSHCrack
from windows.WindowTerminalHistory import WindowTerminalHistory
from windows.WindowGesture import WindowGesture
from windows.WindowNuclearCode import WindowNuclearCode
from Device import Device
from configuration import dimensions, window_properties, relpath

gui = GUI()

# Quest
gui.add_window("quest", WindowQuest(dimensions["width"], dimensions["q_height"], (dimensions["width"],0), "w.quest", label="Quest", **window_properties))
gui.setup_window("quest")

# Network Map
gui.add_window("networkmap", WindowNetworkMap(dimensions["width"], dimensions["nm_height"], (0, dimensions["fe_height"]), "w.networkmap", label="Network map", **window_properties))
# Všechna zařízení přístupná ve hře
# Syntax: název, ip, ikona (path), filesystem (path)
gui.windows["networkmap"].set_devices([
    Device("localhost", "192.168.0.69", relpath("resources/images/desktop.png"), relpath("resources/filesystems/1-localhost.json")),
    Device("HomeServer", "192.168.0.103", relpath("resources/images/server1.png"), relpath("resources/filesystems/2-vlastniserver.json")),
    Device("TestServer", "103.101.45.120", relpath("resources/images/server2.png"), relpath("resources/filesystems/3-ciziserver.json")),
    Device("DontThinkPad", "85.45.120.95", relpath("resources/images/laptop.png"), relpath("resources/filesystems/4-hackerlaptop.json")),
    Device("Roman`s uPhone", "65.42.240.120", relpath("resources/images/phone.png"), relpath("resources/filesystems/5-hackerphone.json"))
])
gui.setup_window("networkmap")

# Historie příkazů terminálu
gui.add_window("history", WindowTerminalHistory(dimensions["width"], dimensions["t_height"], (dimensions["width"],dimensions["q_height"]), "w.history", label="Terminal history", show=False, no_resize=True, no_move=True, no_collapse=True))
gui.setup_window("history")

# Input (pod Terminálem)
gui.add_window("input", WindowInput(dimensions["width"], dimensions["i_height"], (dimensions["width"],dimensions["q_height"]+dimensions["t_height"]), "w.input", **window_properties))
gui.setup_window("input")

# Terminál
gui.add_window("terminal", WindowTerminal(dimensions["width"], dimensions["t_height"], (dimensions["width"],dimensions["q_height"]), "w.terminal", label="Terminal", **window_properties))
gui.setup_window("terminal")

# napojení terminálu na input (spustit metodu patřící terminálu pokaždé, když se v inputu dá Enter)
gui.windows["input"].set_callback("i.input", gui.windows["terminal"].run)

# napojení terminálu na historii
gui.windows["terminal"].set_h_callback(gui.windows["history"].update_run_history)

#předání jmen a IP adres terminálu
gui.windows["terminal"].set_devices([(d.ip, d.name) for d in gui.windows["networkmap"].devices])

# napojení terminálu na network mapu pro network connect
gui.windows["terminal"].set_nm_button_press(gui.windows["networkmap"].force_connect)

# napojení network mapy na terminál - změna filesystému se musí promítnout do zařízení
gui.windows["terminal"].set_nm_callback(gui.windows["networkmap"].update_filesystem)

# napojení terminálu na network mapu - echo
gui.windows["networkmap"].set_terminal_echo(gui.windows["terminal"].cmd_echo)

# File Explorer
gui.add_window("fileexplorer", WindowFileExplorer(dimensions["width"], dimensions["fe_height"], (0,0), "w.fileexplorer", label="File explorer", **window_properties))
# Max res obrazku 400x400
gui.windows["fileexplorer"].set_image_names("kocka1-min.png","kocka2-min.png","kocka3-min.png","kocka4-min.png","kocka5-min.png","pes1-min.png","pes2-min.png","bumprask.png","gratulujeme.png","bitcoin.png","hackers.png","Screenshot_1.png","tierlist.png","waterfall.png")
gui.setup_window("fileexplorer")

# napojení file exploreru na network mapu (při kliknutí na zařízení načíst právě to zařízení)
for device in gui.windows["networkmap"].devices:
    gui.windows["networkmap"].set_callback(f"nm.button-{device.name}", lambda s,a,u: (gui.windows["fileexplorer"].filesystem_load(s,a,u), gui.windows["terminal"].filesystem_load(s,a,u)))

# napojení network mapy na file explorer - změna filesystému se musí promítnout do zařízení
gui.windows["fileexplorer"].set_nm_callback(gui.windows["networkmap"].update_filesystem)

# SSHCrack
gui.add_window("sshcrack", WindowSSHCrack(dimensions["width"], dimensions["ssh_g_c_height"], (0,0), "w.sshcrack", label="SSH Crack", show=False, **window_properties))
gui.setup_window("sshcrack")

# GestureHack
gui.add_window("gesturehack", WindowGesture(dimensions["width"], dimensions["ssh_g_c_height"], (0,0), "w.gesture", label="GestureHack", show=False, **window_properties))
gui.setup_window("gesturehack")

# BSI jaderný kód
gui.add_window("nuclear", WindowNuclearCode(dimensions["width"], dimensions["ssh_g_c_height"], (0,0), "w.nuclear", label="Solospeak - konverzace s uživatelem Bezpečnost Služeb Informatiky", show=False, **window_properties))
gui.setup_window("nuclear")

# Login
gui.add_window("login", WindowLogin(dimensions["l_width"], dimensions["l_height"],
    (((dimensions["v_width"]-dimensions["l_width"])//2), ((dimensions["v_height"]-dimensions["l_height"])//2)),
    "w.login", label="Login", modal=True, **window_properties))
gui.windows["login"].set_gui_level_progress(gui.check_level_progress)
gui.setup_window("login")
gui.set_modal_theme("w.login")

# všechna okna - odkaz na GUI pro změnu levelu
for window in gui.windows.values():
    window.set_progress_function(gui.progress)

gui.event_loop()
