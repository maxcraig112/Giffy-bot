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

from gif import *

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
    given a file of gif urls, replaces all cdn.discordapp.com url prefixes with media.discordapp.com, edit tenor gifs and removes any duplicates
    """
    old_urls = []
    with open(file_name,"r") as f:
        old_urls = f.readlines()
    for i in range(len(old_urls)):
        old_urls[i] = ast.literal_eval(old_urls[i])
    new_urls = []
    c = 0
    for i in old_urls:
        try:
            print(f"{c}/{len(old_urls)}")
            if i[0][:26] == "https://cdn.discordapp.com":
                i[0] = "https://media.discordapp.net" + i[0][26:]
            if "tenor" in i[0] and "c.tenor" not in i[0]:
                #use BS4 to find exact url from html
                r = requests.get(i[0], stream=True)
                soup = BeautifulSoup(r.content, features="html.parser")
                res = soup.findAll('div' , class_="Gif")
                i[0] = res[0].img['src']
            if i not in new_urls:
                new_urls += [i]
        except:
            print(f"{i[0]}")
        c += 1
    with open(file_name, "w") as f:
        for i in new_urls:
            f.write(f"{i}\n")

def process_url(url_data, caption_json_file, uncaption_json_file, tags_json_file):
    """
    given a url directory, downloads the image, processing it, obtaining it's metadata, and stores it in it's respective json file if it isn't already in the file.
    """
    #instantiate Gif object
    #open respective json
    
    #if gif exists in global, don't download meta data, otherwise do, and add to global
    #if gif exists in guild, don't download meta data, otherwise do, and add to guild
    #if gif exists in user, don't download meta data, otherwise do, and add to user
    # FOR THESE 3 STEPS: only download meta data once
    try:
        url = AttachmentURL(url_data[0],url_data[1],url_data[2],url_data[3])
        #instantiate gif object
        gif = Gif(url.url,auto_download=True)
        if gif.img is not None:
            metadata = [url.guildID,url.channelID,url.userID]
            #if gif is a caption gif
            if gif.is_caption_gif():
                caption = gif.text_from_caption() #get caption
                tags = Tagger(caption).tags #get tags
                stats = gif.stats()
                metadata += [caption,tags,stats]
                #await message.channel.send(tags)
                tags_json = JsonGifs(tags_json_file)
                for tag in tags:
                    tags_json.set_catagory('global')
                    tags_json.addsubKey(tag)
                    if not tags_json.contains(url.url,subkey=tag):
                        tags_json.add(url.url,metadata[:-3],tag)
                    tags_json.set_catagory('guild')
                    tags_json.addsubKey(url.guildID)
                    tags_json.addsubsubKey(url.guildID,tag)
                    if not tags_json.contains(url.url,url.guildID,tag):
                        tags_json.add(url.url,metadata[:-3],url.guildID,tag)
                    tags_json.set_catagory('user')
                    tags_json.addsubKey(url.userID)
                    tags_json.addsubsubKey(url.userID,tag)
                    if not tags_json.contains(url.url,url.userID,tag):
                        tags_json.add(url.url,metadata[:-3],url.userID,tag)
                tags_json.dump_json()

            #instantiate json archiving object, file open depends on whether gif contains a caption
            archives = JsonGifs(caption_json_file if gif.is_caption_gif() else uncaption_json_file,"global")
            if not archives.contains(url):
                archives.add(url.url,metadata) #add url to global key
            #print(archives.contains_alt_url(url))
            archives.set_catagory("guild") #set catagory to guild key
            
            archives.addsubKey(url.guildID) #if server ID not in guild key, add, then add url to server ID
            if not archives.contains(url.url,url.guildID):
                archives.add(url.url,None,url.guildID)
            #print(archives.contains_alt_url(url,url.guildID))
            archives.set_catagory("user") #if user ID not in user key, add, then add url to user ID
            
            archives.addsubKey(url.userID)
            if not archives.contains(url.url,url.userID):
                archives.add(url.url,None,url.userID)
            #print(archives.contains_alt_url(url,url.userID))
            archives.dump_json() #save json file
            return None
    except Exception as e:
        print(e)
        print(url_data[0])
        return url_data

def add_metadata(file_name, guild_ID, channel_ID, user_ID):
    with open(file_name,"r") as f:
        gifs = f.readlines()
    for i in range(len(gifs)):
        gifs[i] = [gifs[i][:-1],str(guild_ID),str(channel_ID),str(user_ID)]
    
    with open(file_name, "w") as f:
        for i in gifs:
            f.write(f"{i}\n")

def convert_csv(file_name):
    """
    Take a filename for a csv file generated by the Discord Chat Exporter, filter all of the messages to only include valid gif urls, with no duplicates.

    Conversion and metadata can be added in seperate methods
    """
    with open(file_name,"r",encoding="utf8") as f:
        lines = f.readlines()[1:]
    urls = set()
    for i in lines:
        if validators.url(i[:-1]) and (i[:-1][-4:] == ".gif" or "tenor" in i):
            urls.add(i[:-1])
    #print(urls)
        #attachment = data[4][1:-1]
    with open("URLS.txt", "w") as f:
        for i in urls:
            f.write(f"{i}\n")

        
    pass
if __name__ == "__main__":
    # save_all_gifs("All gifs/all_regular_gifs.txt","Json/archivedgifs.json")
    #save_all_gifs("All gifs/all_caption_gifs.txt","Json/archivedcaptiongifs.json")
    #convert_gifs("All gifs/all_regular_gifs.txt")
    #convert_gifs("All gifs/all_caption_gifs.txt")
    #add_metadata("All Gifs/alex.txt",868888972120702996,868888972120702999,179894333275766784)
    #convert_gifs("All gifs/alex.txt")
    
    #convert_csv("All gifs/General Sam General CONTENT.csv")
    add_metadata("URLS.txt","294521277941678080","806714809462161478","227968197129797632")
    convert_gifs("URLS.txt")

    # caption_gifs = []
    # with open("All gifs/alex.txt","r") as f:
    #     caption_gifs = f.readlines()
    # for i in range(len(caption_gifs)):
    #     caption_gifs[i] = ast.literal_eval(caption_gifs[i])

    # failed_gifs = []
    # for i in range(len(caption_gifs)):
    #     #print(caption_gifs[i])
    #     print(f"{i}/{len(caption_gifs)}")
    #     gif = process_url(caption_gifs[i],"Json/archivedcaptiongifs.json","Json/archivedgifs.json","Json/tags.json")
    #     if gif != None:
    #         failed_gifs += [gif]
    
    # print("ITS FUCKING DONE, POG POG POG POG POG POG")
    # with open("failed_gifs.txt","w") as f:
    #     for i in failed_gifs:
    #         f.write(f"{i}\n")
    