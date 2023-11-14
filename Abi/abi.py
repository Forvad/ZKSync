from json import load
from os import listdir, getcwd
from os.path import isfile, join
from sys import platform


def open_abi(mode='') -> {str: str}:
    try:
        add_patch = '/Abi' if platform == "linux" and 'darwin' else '\\Abi'
        mypath = getcwd() + add_patch
        list_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        abi_ = {}
        for file in list_files:
            if 'json' in file:
                with open(mode + file, "r") as f:
                    abi_Merkly = load(f)
                    abi_[file.replace('.json', '').replace('./Abi/', '')] = abi_Merkly
        return abi_
    except FileNotFoundError:
        return open_abi(mode='./Abi/')


ABI = open_abi()
