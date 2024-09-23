from os import path, sep as pathseparator
from json import loads as jsonloads
from cryptography.fernet import Fernet
from hashlib import sha512

from configuration import relpath, FERNET_KEY

userfile_name = path.expanduser("~") + pathseparator + "user.htest"

fernet = Fernet(FERNET_KEY)

#funkce pro práci se save souborem
def userfile_load() -> dict:
    with open(userfile_name, mode="rb") as userfile:
        userdata = jsonloads(str(fernet.decrypt(userfile.read()), encoding="utf-8")) 
    return userdata
    #fernet pracuje jen s byte stringy/soubory, takže nejde načíst rovnou slovník

#NEPOUŽÍVAT PRO PROGRESS, při split_frame to může způsobit, že se přepíše jedna věc a ne ta druhá
def userfile_edit(value: str|int, field: str) -> None:
    with open(userfile_name, mode="rb+") as userfile:
        data = jsonloads(str(fernet.decrypt(userfile.read()), encoding="utf-8"))
        data[field] = value
        userfile.seek(0)
        userfile.write(b"") #nastaví pozici na 0 a zapíše prázdný byte string => vymaže obsah souboru
        data = fernet.encrypt(bytes(str(data).replace("'", '"'), encoding="utf-8"))
        userfile.write(data)
        #převádění slovníku na string nahradí všechy uvozovky těmito --> '
        #problém je že JSON umí používat jenom --> " <-- takže by to při načtení crashlo
        #ukládaná data tím pádem NIKDY nesmí obsahovat ", ', pro jistotu ani \

def userfile_overwrite(data: dict) -> None:
    data = fernet.encrypt(bytes(str(data).replace("'", '"'), encoding="utf-8"))
    with open(userfile_name, mode="wb") as userfile:
        userfile.write(data)

#spustí se při každém otevření hry
def userfile_check() -> int: 
    if path.exists(userfile_name): #  Arbitrary filename coz why not
        try:
            userfile_load()
            return 1 #soubor existuje, načteno
        except Exception:
            return -2 #soubor se nepodařilo načíst (způsobeno např. uživatelskou úpravou šifrovaných dat)
    return 0 #soubor neexistuje

#hodně se podobá userfile_edit, ale nemělo by dělat problémy u split_frame, protože se level a quest změní současně
def userfile_progress(level: int, quest: int):
    with open(userfile_name, mode="rb+") as userfile:
        data = jsonloads(str(fernet.decrypt(userfile.read()), encoding="utf-8"))
        data["level"] = level
        data["quest"] = quest
        userfile.seek(0)
        userfile.write(b"") #nastaví pozici na 0 a zapíše prázdný byte string => vymaže obsah souboru
        data = fernet.encrypt(bytes(str(data).replace("'", '"'), encoding="utf-8"))
        userfile.write(data)

def create_hash(text: str) -> str:
    text += "bruh"
    return sha512(text.encode("utf-8")).hexdigest()
