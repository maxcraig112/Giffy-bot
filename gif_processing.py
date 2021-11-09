from enum import auto
import PIL
from bs4 import *
from io import BytesIO, StringIO
import os
from numpy.core.fromnumeric import mean
from numpy.lib.twodim_base import triu_indices_from
import validators
import uuid
from typing import Text
import requests
import urllib.request
from shutil import *
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageStat import Stat
import numpy as np
from pytesseract import *
import math
from URLJson import *
import timeit
from difflib import SequenceMatcher
import ast

def save_all_gifs(file_name,json_file,store_metadata=True):
    """
    From a specified json_file, downloads all gifs url within the "global" subdictionary and it's attachment metadata, and stores them in the designated file
    """
    with open(file_name, "w") as f:
        gifs_json = JsonGifs(json_file)
        gifs_json.set_catagory("global")
        print("Number of gifs: " + str(len(gifs_json.subdict)))
        start = timeit.default_timer()
        for i in gifs_json.subdict:
            if store_metadata:
                f.write(f"{[i,gifs_json.subdict[i][0],gifs_json.subdict[i][1],gifs_json.subdict[i][2]]}\n")
            else:
                f.write(f"{i}\n")
        print("Time taken: " + str(round(timeit.default_timer() - start,2)))

def convert_gifs(file_name):
    """
    given a file of gif urls, replaces all cdn.discordapp.com url prefixes with media.discordapp.com, and removes any duplicates
    """
    old_urls = []
    with open(file_name,"r") as f:
        old_urls = f.readlines()
    for i in range(len(old_urls)):
        old_urls[i] = ast.literal_eval(old_urls[i])
    new_urls = []
    for i in old_urls:
        if i[0][:26] == "https://cdn.discordapp.com":
            i[0] = "https://media.discordapp.net" + i[0][26:]
        if i not in new_urls:
            new_urls += [i]
    with open(file_name, "w") as f:
        for i in new_urls:
            f.write(f"{i}\n")

def process_url(url, caption_json, uncaption_json, tags_json):
    """
    given a url directory, downloads the image, processing it, obtaining it's metadata, and storing it in it's respective json file if it isn't already in the file.
    """
    pass


if __name__ == "__main__":
    save_all_gifs("All gifs/all_regular_gifs.txt","Json/archivedgifs.json")
    save_all_gifs("All gifs/all_caption_gifs.txt","Json/archivedcaptiongifs.json")
    convert_gifs("All gifs/all_regular_gifs.txt")
    convert_gifs("All gifs/all_caption_gifs.txt")
    
    
    # f = open("All gifs/maxgifs.txt","r")
    # g = open("All gifs/tainegifs.txt","r")
    # gif1 = f.readlines()
    # gif2 = g.readlines()
    # for i in range(len(gif1)):
    #     gif1[i] = [gif1[i].strip(),470896999722516480,514393245191634947,217233850101661697]
    # for i in range(len(gif2)):
    #     gif2[i] = [gif2[i].strip(),470896999722516480,514393245191634947,158878635766317056]
    # combined = gif1 + gif2
    # with open("All gifs/maxtainegifs.txt","w") as h:
    #     for i in combined:
    #         h.write(f"{i}\n")



    pass