import dearpygui.dearpygui as dpg

class Timer:
    def __init__(self, interval):
        self.total_time = dpg.get_total_time()
        self.last_total_time = dpg.get_total_time()
        self.interval = interval

    def update(self):
        self.total_time = dpg.get_total_time()
        delta_time = dpg.get_total_time() - self.last_total_time
        if delta_time > self.interval:
            self.last_total_time = self.total_time
            return True
        return False

#s/o Dear PyGui Discord za tento kód
#potřeba pro vykonávání něčeho v render loopu v nějakém intervalu
