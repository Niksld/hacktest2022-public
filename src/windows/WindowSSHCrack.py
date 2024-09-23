from lib2to3.pgen2.pgen import generate_grammar
import dearpygui.dearpygui as dpg

from windows.Window import Window
from random import choice, randint
from configuration import sshcrack_conf

class WindowSSHCrack(Window):
    def __init__(self, width: int, height:int, pos: tuple[int, int], tag: str, **kwargs):
        super().__init__(width, height, pos, tag, **kwargs, no_title_bar=False)
        self.width = width - 30
        self.node_links = {}
        
        #  Vytvori pro kazdy node_attribute polozku,
        #  ukladaji se s cim je kazda node_attr spojena
        for i in range(6):
            self.node_links.update({f"ssh.node{i}.attr":None})
        self.problems = {}
        self.node_links_correct = {}   
         
        for i in range(6):
            self.node_links_correct.update({f"ssh.node{i}.attr":False})
        
    def on_complete(self):
        self.update_problems()
        match self.level, self.quest:
            case (3, 0) | (3, 1):
                self.progress(4, 0)
            
            case 4, 1:
                self.progress(4, 2)
    
    def check_link(self,node1,node2):
        operants = ['+','-','/','*']
        key = None
        value = None
        for i in range(4):
            if operants[i] in node1:
                key = node1
                value = node2
        else:
            key = node2
            value = node1
        
        # print("dict_key_check " + str(self.problems[dpg.get_value(f"{value}.text")]) + "value " +str(dpg.get_value(f"{key}.text")))
        if str(self.problems[dpg.get_value(f"{value}.text")]) == str(dpg.get_value(f"{key}.text")):
            self.node_links_correct[node1] = True
            self.node_links_correct[node2] = True
        
        dict_values = list(self.node_links_correct.values())
        
        count_true = 0
        
        for i in range(len(self.node_links_correct)):
            if dict_values[i] == True:
                count_true += 1
        
        if count_true == 6:
            dpg.configure_item("w.sshcrack", show=False)
            
            dict_keys = list(self.node_links.keys())
            # print(f"DictKeys {dict_keys}")
            for i in range(3):
                # print(f"{dict_keys[i]}, {self.node_links[dict_keys[i]]}")
                dpg.delete_item(f"{dict_keys[i]}, {self.node_links[dict_keys[i]]}")
            for i in range(6):
                self.node_links[dict_keys[i]] = None
                self.node_links_correct[dict_keys[i]] = False
            
            self.on_complete()
            
        # print(f"count true {count_true}")
        
    #  Callback na spojeni 2 node_attributů
    def link_callback(self,sender, app_data):
        # app_data -> (link_id1, link_id2)
        
        if self.node_links[app_data[0]] == None and self.node_links[app_data[1]] == None:
            dpg.add_node_link(app_data[0], app_data[1], parent=sender,tag=f"{app_data[0]}, {app_data[1]}")
            self.node_links[app_data[0]] = app_data[1]
            self.node_links[app_data[1]] = app_data[0]
            self.check_link(app_data[0],app_data[1])
    
    #  Callback na rozpojeni 2 attributů
    def delink_callback(self, sender, app_data):
        # app_data -> link_id
        prasarna = tuple(map(str, app_data.split(", "))) # :) vraci tuple
        dpg.delete_item(app_data)
        self.node_links[prasarna[0]] = None
        self.node_links[prasarna[1]] = None
        self.node_links_correct[prasarna[0]] = False
        self.node_links_correct[prasarna[1]] = False
        
    def generate_problem(self):
        num1, num2 = randint(0,100), randint(1,100)
        operant = choice(["+","-","*","/"])
        match operant:
            case "+":
                self.problems.update({f"{num1}+{num2}":(num1+num2)})
                return [f"{num1}+{num2}",(num1+num2)]
            case "-":
                self.problems.update({f"{num1}-{num2}":(num1-num2)})
                return [f"{num1}-{num2}",(num1-num2)]
            case "/":
                self.problems.update({f"{num1}/{num2}":round((num1/num2),4)})
                return [f"{num1}/{num2}",round((num1/num2),4)]
            case "*":
                self.problems.update({f"{num1}*{num2}":(num1*num2)})
                return [f"{num1}*{num2}",(num1*num2)]
            
    def update_problems(self):
        problems_q = []
        problems_a = []
        for i in range(3):
            temp_problem = self.generate_problem()
            problems_q.append(temp_problem[0])
            problems_a.append(temp_problem[1])
        
        picking_list = problems_q
        for i in range(6):
            if i == 3:
                picking_list = problems_a
            pick = choice(picking_list)
            dpg.set_value(f"ssh.node{i}.attr.text",pick)
            picking_list.remove(pick)

    def setup(self):
        attribute_setting = dpg.mvNode_Attr_Output
        x_pos = sshcrack_conf['x_pos_r1']
        
        dpg.add_text("Spoj tečky u příkladů nalevo s tečkami výsledků napravo. Pokud uděláš chybu, podrž CTRL a klikni na čáru pro její odstranění.", tag="ssh.guide", wrap=self.width)
        
        with dpg.node_editor(callback=self.link_callback, delink_callback=self.delink_callback, tag="ssh.nodeeditor"):
            for i in range(6):
                if i == 3:
                    attribute_setting = dpg.mvNode_Attr_Input
                    x_pos = sshcrack_conf['x_pos_r2']
                
                with dpg.node(label=f"SSHnode {i}", tag=f"ssh.node{i}", pos=(x_pos,sshcrack_conf['y_pos'][i]), draggable=False):
                    with dpg.node_attribute(label=f"Node A{i}" , attribute_type=attribute_setting, tag=f'ssh.node{i}.attr'):
                        dpg.add_text(f"Node text{i}",tag=f"ssh.node{i}.attr.text")
        self.update_problems()
                

 
