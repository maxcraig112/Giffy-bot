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

def save_all_gifs(file_name,json_file):
    """
    From a specified json_file, downloads all gifs url within the "global" subdictionary, and stores them in the designated file
    """
    with open(file_name, "w") as f:
        gifs_json = JsonGifs(json_file)
        gifs_json.set_catagory("global")
        print("Number of gifs: " + str(len(gifs_json.subdict)))
        start = timeit.default_timer()
        for i in gifs_json.subdict:
            f.write(f"{i}\n")
        print("Time taken: " + str(round(timeit.default_timer() - start,2)))

def convert_gifs(file_name):
    """
    given a file of gif urls, replaces all cdn.discordapp.com url prefixes with media.discordapp.com, and removes any duplicates
    """
    old_urls = []
    with open(file_name,"r") as f:
        old_urls = f.readlines()
    new_urls = []
    for i in old_urls:
        if i[:26] == "https://cdn.discordapp.com":
            i = "https://media.discordapp.net" + i[26:]
        if i not in new_urls:
            new_urls += [i]
    with open(file_name, "w") as f:
        for i in new_urls:
            f.write(f"{i}")

def process_url(urls_filename, caption_json, uncaption_json, tags_json):
    """
    given a url directory, downloads the image, processing it, obtaining it's metadata, and storing it in it's respective json file if it isn't already in the file.
    """
    pass


if __name__ == "__main__":
    #save_all_gifs("All gifs/all_regular_gifs.txt","Json/archivedgifs.json")
    #convert_gifs("All gifs/all_regular_gifs.txt")
    pass