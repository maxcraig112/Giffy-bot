import json
from re import sub
from bs4 import *
from io import BytesIO, StringIO
import os
import validators
import uuid
import requests
import urllib.request
from shutil import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
from pytesseract import *
#from gif import Gif
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
    
    def contains(self, item, subkey= None, subsubkey= None):
        if subkey == None:
            return item in self.subdict
        if subsubkey == None:
            return item in self.subdict[subkey]
        return item in self.subdict[subkey][subsubkey]
    
    def addsubKey(self,keyName):
        """
        Creates a new subkey inside the subdictionary
        Useful for adding guild ID's to guild or user ID's to user

        if subKey already exists, return None
        """
        if self.contains(keyName):
            return None
        self.add(keyName,{})
    
    def addsubsubKey(self,subKey,subsubKey):
        """
        Creates a new subsubkey inside the dictionary
        useful for adding new tags
        """
        if self.contains(subsubKey,subKey):
            return None
        self.add(subsubKey,{},subKey)

    def add(self, item, data = None, subkey = None,subsubkey=None):
        if self.subdict != None:
            if subkey == None:
                if not self.contains(item):
                    self.subdict[item] = data
            else:
                if subsubkey == None:
                    if not self.contains(item,subkey):
                        self.subdict[subkey][item] = data
                else:
                    if not self.contains(item,subkey,subsubkey):
                        self.subdict[subkey][subsubkey][item] = data
    
    def set_file_name(self, new_file_name):
        if new_file_name[-5:].lower() == ".json":
            self.file_name = new_file_name
    
    def _update_dict(self):
        if self.key != None:
            self.dict[self.key] = self.subdict
    
    def __len__(self):
        return len(self.subdict)

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
    
    def contains_alt_url(self, url, subkey=None,subsubkey=None):
        contains = False
        if len(url.url) > 39 and url.url[:39] == "https://cdn.discordapp.com/attachments/":
            if self.contains("https://media.discordapp.net/attachments/"+url.url[39:],subkey=subkey,subsubkey=subsubkey):
                    contains = True
        if len(url.url) > 41 and url.url[:41] == "https://media.discordapp.net/attachments/":
            if self.contains("https://cdn.discordapp.com/attachments/"+url.url[:41],subkey=subkey,subsubkey=subsubkey):
                    contains = True
        return contains
    
class Tagger:
    def __init__(self, caption) -> None:
        self.caption = caption
        self.tags = self._process_caption()

    def _process_caption(self):
        #remove non unicode characters
        text = self.caption.encode("ascii","ignore")
        text = text.decode()
        #remove all symbols
        text = ''.join(ch for ch in text if (ch.isalnum() or ch == " "))
        #tokenize and get word types
        tokens = word_tokenize(text)
        alltags = nltk.pos_tag(tokens)
        #get stop words
        #stop_words = set(stopwords.words("english"))
        stop_words = ['him', 'only', 'been', 'on', 'such', 'isn', 'were', "wasn't", 'hadn', 've', 'shouldn', 'those', 'other', 'not', "won't", 'hasn', "doesn't", 'over', "didn't", 'below', 'now', 'after', 'is', "she's", 'each', 'this', 'what', "needn't", 'your', 'theirs', 'doesn', 'wasn', 'couldn', 'which', 'do', 'their', 'll', 'at', 'to', "that'll", "isn't", 'in', 'and', "don't", 'ain', 'weren', 'myself', 'most', "couldn't", 'yourselves', "mightn't", 'further', "shouldn't", 'can', 'before', 'he', "mustn't", 'should', "hasn't", 'a', 'or', 'of', 'won', 'nor', 'hers', 's', 'them', 'aren', 'by', 'mightn', 'herself', 'she', "you're", 'it', 'about', "should've", 'all', 'have', 'both', "hadn't", 'between', 'itself', 'for', "weren't", 'above', "shan't", 'while', 'under', 'down', 'there', 'ma', 'our', 'am', 'has', 'because', 'when', 't', 'does', 'where', 'then', 'very', 'why', 'any', 'mustn', 'some', 'himself', 'out', 'whom', 'who', 'if', 'm', 'don', 're', 'the', 'so', 'his', 'wouldn', "you'd", "aren't", 'until', 'an', 'we', 'off', 'themselves', 'me', 'did', 'had', 'you', "you'll", 'against', 'through', 'again', 'will', 'how', "haven't", 'needn', 'that', "wouldn't", 'haven', 'with', "it's", 'from', 'too', 'its', 'i', 'more', 'are', 'be', 'didn', "you've", 'but', 'they', 'as', 'o', 'was', 'these', 'here', 'than', 'y', 'up', 'few', 'yourself', 'shan', 'her', 'once', 'my', 'own', 'ourselves', 'same', 'yours', 'into', 'ours', 'd', 'just', 'no']
        #stop_words = ""
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
            #if correct word type, tag not already included and len is > 1
            if i[1][0] in ["J","N","V","I","D"] and i[0].lower() not in final_tags and len(i[0]) > 1:
                final_tags += [i[0].lower()]
        #print(final_tags)
        return final_tags
        


if __name__ == "__main__":
   tag = Tagger("max building essential highway infrastructure for the working class (they need fo commute to the CED) (Central Emerald District) while his entire team fails to defend the bed (they are very bad)")
   print(tag.tags)
    # captiongifs = JsonCaptionGifs("test.json")
    # captiongifs.set_catagory("global")
    # print(captiongifs.subdict)
    # captiongifs.set_catagory("guild")
    # print(captiongifs.subdict)
    # captiongifs.set_catagory("user")
    # print(captiongifs.subdict)
