import json
from bs4 import *
from io import BytesIO, StringIO
import os
import validators
import uuid
from typing import Text, final
import requests
import urllib.request
from shutil import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
from pytesseract import *
from gif import Gif
from enum import Enum
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords

class AttachmentURL:
    def __init__(self, url, guildID = None, channelID = None, userID = None) -> None:
        self.url = url
        self.guildID = str(guildID)
        self.channelID = str(channelID)
        self.userID = str(userID)

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
    
    def addsubKey(self,keyName):
        """
        Creates a new subkey inside the subdictionary
        Useful for adding guild ID's to guild or user ID's to user

        if subKey already exists, return None
        """
        if self.contains(keyName):
            return None
        self.add(keyName,{})

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
    
class Tagger:
    def __init__(self, caption) -> None:
        self.caption = caption
        self.tags = self._process_caption()

    def _process_caption(self):
        text = self.caption.encode("ascii","ignore")
        text = text.decode()
        tokens = word_tokenize(text)
        alltags = nltk.pos_tag(tokens)
        stop_words = set(stopwords.words("english"))
        #print(alltags)
        sub_tags = []
        #remove all tags that are stop_words
        for i in alltags:
            if i[0].lower() not in stop_words:
                sub_tags += [i]
        #print(sub_tags)
        

        final_tags = []
        #remove all tags that aren't nouns, adjectives, verbs, and add only lowercase words to final_tags
        for i in sub_tags:
            if i[1][0] in ["J","N","V"] and i[0].lower() not in final_tags:
                final_tags += [i[0].lower()]
        #print(final_tags)
        return final_tags
        


if __name__ == "__main__":
   tag = Tagger("Releasing my 9 (sex ‘antoni is gay‘)trillion trained fire ants on the homeless man who was blinking my coordinates in binary to my gangstalkers")
    # captiongifs = JsonCaptionGifs("test.json")
    # captiongifs.set_catagory("global")
    # print(captiongifs.subdict)
    # captiongifs.set_catagory("guild")
    # print(captiongifs.subdict)
    # captiongifs.set_catagory("user")
    # print(captiongifs.subdict)