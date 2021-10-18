import json
from bs4 import *
from io import BytesIO, StringIO
import os
import validators
import uuid
from typing import Text
import requests
import urllib.request
from shutil import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
from pytesseract import *
from gif import Gif
from enum import Enum

class URLCatagories(Enum):
    Global = "global"
    Guild = "guild"
    User = "user"

class Json:
    def __init__(self,file_name) -> None:
        self.file_name = file_name
        self.dict = self._load_json()
        self.subdict = None
        self.key = None

    def _load_json(self):
        """
        Opens JSON file and returns a dictionary of contained data
        """
        with open(self.file_name, "r") as f:
            dict = json.load(f)
            return dict
        
    def dump_json(self):
        """
        Opens JSON file and dumps dictionary data
        """
        self._update_dict()
        with open(self.file_name,"w") as fw:
            json.dump(self.dict, fw, indent=4)
    
    def contains(self, item, subkey= None):
        if subkey == None:
            return item in self.subdict
        return item in self.subdict[subkey]
    
    def add(self, item, data = None, subkey = None):
        if self.subdict != None:
            if subkey == None:
                if not self.contains(item):
                    self.subdict[item] = data
            else:
                if not self.contains(item,subkey):
                    self.subdict[subkey][item] = data
    
    def set_file_name(self, new_file_name):
        if new_file_name[-5:].lower() == ".json":
            self.file_name = new_file_name
    
    def _update_dict(self):
        if self.key != None:
            self.dict[self.key] = self.subdict

class JsonGifs(Json):

    def __init__(self,file_name,key = None) -> None:
        Json.__init__(self,file_name)
        if key != None:
            self.key = self.set_catagory(key)

    def set_catagory(self, catagory):
        """
        Returns the dictionary of urls contained within the catagory
        """
        try:
            c = URLCatagories(catagory.lower())
            self._update_dict()
            self.subdict = self.dict[catagory.lower()]
            self.key = catagory
            return catagory.lower()
        except ValueError:
            return None
    
if __name__ == "__main__":
   pass
    # captiongifs = JsonCaptionGifs("test.json")
    # captiongifs.set_catagory("global")
    # print(captiongifs.subdict)
    # captiongifs.set_catagory("guild")
    # print(captiongifs.subdict)
    # captiongifs.set_catagory("user")
    # print(captiongifs.subdict)