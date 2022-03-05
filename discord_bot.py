from email.mime import image
import json
import os
import random
from re import M, search
from typing import Dict
from numpy import true_divide

from numpy.lib.function_base import median
from gif import Gif
from validators.url import url
import discord
import validators
from discord import Colour, Embed
from discord.ext import commands
from discord.ui import Button, View
from URLJson import *
import timeit
from copy import copy
from statistics import mean
import time

def run_bot(TOKEN):

    client = commands.Bot(command_prefix=".")
    CAPTION_MADE = False
    def get_last(message):
        #get the last gif which was posted into the server
            with open("Json/lastgif.json", "r") as f:
                dict = json.load(f)
                try:
                    gif = dict[str(message.guild.id)][str(message.channel.id)]
                    return gif
                except KeyError:
                    return None

    def get_last_search(search_ID,guild_ID,channel_ID,user_ID):
        #get the last search which was posted in scope by user
        with open("Json/lastsearch.json", "r") as f:
            dict = json.load(f)
            try:
                search_data = dict[guild_ID][channel_ID][user_ID]
                return search_data
            except KeyError:
                return None

    async def no_gif_found(message):
        await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")
    
    async def resize_and_send(gif, message):
        gif.save(f"{message.channel.id}_{message.guild.id}.gif")
        while os.path.getsize(f"{message.channel.id}_{message.guild.id}.gif") > 8000000:
            #await message.channel.send("Caption too big! resizing!")
            gif = Gif(f"{message.channel.id}_{message.guild.id}.gif")
            print("resizing")
            gif.resize(0.75)
            gif.save(f"{message.channel.id}_{message.guild.id}.gif")
        await message.channel.send(file=discord.File(f"{message.channel.id}_{message.guild.id}.gif"))
        del gif
        os.remove(f"{message.channel.id}_{message.guild.id}.gif")

    def gif_is_sent(message):
        if len(message.attachments) > 0 and os.path.splitext(message.attachments[-1].filename)[-1] == ".gif": # validators.url(message.attachments[-1].url) and 
            return message.attachments[-1].url
        if validators.url(message.content) and (message.content[-4:] == ".gif" or "tenor" in message.content):
            return message.content
        return None

    def last_search_json(search_ids: str,guild_id: str,channel_id: str,user_id: str,gifs: list,index: int):
        f = open("Json/lastsearch.json","r")
        dict = json.load(f)
        if guild_id not in dict:    #if json database does not have key for current server
            dict[guild_id] = {}     #add current server to json database
        
        if channel_id not in dict[guild_id]: #if json database does not have key for current channel
            dict[guild_id][channel_id] = {} #add current channel to json database
        #add url to key of channel.id. whether or not it exists, it will be created or placed there
        dict[guild_id][channel_id][str(user_id)] = {"user": str(user_id), "search_id": search_ids, "gifs": gifs, "index": index}
        with open("Json/lastsearch.json","w") as fw:
            json.dump(dict, fw, indent=4)
    
    def last_gif_json(url):
        f = open("Json/lastgif.json","r")
        dict = json.load(f)
        if url.guildID not in dict: #if json database does not have key for current server
            dict[url.guildID] = {}  #add current server to json database
        #add url to key of channel.id. whether or not it exists, it will be created or placed there
        dict[url.guildID][url.channelID] = url.url
        with open("Json/lastgif.json","w") as fw:
            json.dump(dict, fw, indent=4)

    def store_gif(url,gif,data):
        if gif.is_caption_gif():
            if len(data) == 3:
                caption = gif.text_from_caption() #get caption
                tags = Tagger(caption).tags #get tags
                data += [tags]
            #await message.channel.send(tags)

            tags_json = JsonGifs("Json/tags.json")
            for tag in data[-1]:
                tags_json.set_catagory('global')
                tags_json.addsubKey(tag)
                if not tags_json.contains_alt_url(url,subkey=tag):
                    tags_json.add(url.url,data[:-1],tag)
                tags_json.set_catagory('guild')
                tags_json.addsubKey(url.guildID)
                tags_json.addsubsubKey(url.guildID,tag)
                if not tags_json.contains_alt_url(url,url.guildID,tag):
                    tags_json.add(url.url,data[:-1],url.guildID,tag)
                tags_json.set_catagory('user')
                tags_json.addsubKey(url.userID)
                tags_json.addsubsubKey(url.userID,tag)
                if not tags_json.contains_alt_url(url,url.userID,tag):
                    tags_json.add(url.url,data[:-1],url.userID,tag)
            tags_json.dump_json()

        #instantiate json archiving object, file open depends on whether gif contains a caption
        archives = JsonGifs("Json/archivedcaptiongifs.json" if gif.is_caption_gif() else "Json/archivedgifs.json","global")
        if not archives.contains_alt_url(url):
            archives.add(url.url,data) #add url to global key
        #print(archives.contains_alt_url(url))
        archives.set_catagory("guild") #set catagory to guild key
        
        archives.addsubKey(url.guildID) #if server ID not in guild key, add, then add url to server ID
        if not archives.contains_alt_url(url,url.guildID):
            archives.add(url.url,None,url.guildID)
        #print(archives.contains_alt_url(url,url.guildID))
        archives.set_catagory("user") #if user ID not in user key, add, then add url to user ID
        
        archives.addsubKey(url.userID)
        if not archives.contains_alt_url(url,url.userID):
            archives.add(url.url,None,url.userID)
        #print(archives.contains_alt_url(url,url.userID))

        archives.dump_json() #save json file
    @client.event
    async def on_ready():
        print("Bot is ready")
        activity = discord.Activity(type=discord.ActivityType.watching, name="for any gifs")
        await client.change_presence(status=discord.Status.online,activity=activity)

    @client.event
    async def on_message(message):
        msg = message.content.lower()
        try:
            if msg == ".test":
                gifs = ["https://media.discordapp.net/attachments/712243005519560736/947711699706855474/712243005519560736_470896999722516480.gif","https://tenor.com/view/burrito-pass-peepohappy-gif-18706235","https://media.discordapp.net/attachments/690819748929470475/923615350677991445/rhfp8exd29781.gif"]
                i = 0

                async def prev_gif_callback(interaction):
                    await interaction.response.send_message("previous gif")

                async def next_gif_callback(interaction):
                    await interaction.response.send_message("next gif")
                prev_button = Button(label='Previous Gif',custom_id='prev_gif',style=discord.ButtonStyle.blurple)
                next_button = Button(label='Next Gif',custom_id='next_gif',style=discord.ButtonStyle.blurple)
                prev_button.callback = prev_gif_callback
                next_button.callback = next_gif_callback
                view = View(prev_button,next_button)
                button_msg = await message.channel.send(view=view)
            if msg == ".cgif":
                gif = Gif(get_last(message),auto_download=True)
                #gif._get_image(gif.img_reference)
                if gif.img != None:
                    if gif.is_caption_gif():
                        await message.channel.send("The last gif has a caption")
                    else:
                        await message.channel.send("The last gif does not have a caption")
                else:
                    await no_gif_found(message)
            if msg == ".rgif":
                # open archived gifs, get random url from global
                archive = JsonGifs("Json/archivedgifs.json","global")
                count = 0
                maxx = random.randrange(0,len(archive))
                for i in archive.subdict:
                    if count == maxx:
                        await message.channel.send(i)
                        break
                    count += 1
            if msg == ".rcgif":
                # open archived gifs, get random url from global
                archive = JsonGifs("Json/archivedcaptiongifs.json","global")
                count = 0
                maxx = random.randrange(0,len(archive))
                for i in archive.subdict:
                    if count == maxx:
                        await message.channel.send(i)
                        break
                    count += 1
            if msg == ".text":
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    text = gif.text_from_caption()
                    if text != None:
                        await message.channel.send(text)
                    else:
                        await message.channel.send("no text found")
                else:
                    await no_gif_found(message)
            if msg == ".tags":
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    text = gif.text_from_caption()
                    if text != None:
                        tags = Tagger(text).tags #get tags
                        await message.channel.send(tags)
                else:
                    await no_gif_found(message)
            if msg.split(" ",1)[0] == ".ttags":
                text = msg.split(" ",1)[1]
                print(text)
                tags = Tagger(text).tags #get tags
                await message.channel.send(tags)
            if msg == ".lgif":
                gif = get_last(message)
                if gif != "" and gif != None:
                    await message.channel.send(gif)
                else:
                    await no_gif_found(message)
            if msg[:7] == ".search":
                search_terms = msg[8:].replace(" ","").lower().split(",")
                original_search_terms = search_terms[:]
                for i in range(len(search_terms)):
                    if search_terms[i][-1] != "s":
                        search_terms += [search_terms[i] + "s"]
                urls = []
                scores = []
                max_tags = []

                tags_json = JsonGifs("Json/tags.json","global")
                size = len(tags_json.subdict)
                #for every search term the user inputted
                for term in search_terms:
                    #for every single slice of that search term
                    for i in range(len(term) + 1):
                        #if search term exists in tags
                        if tags_json.contains(term):
                            # yoink every url inside tag, if url has been grabbed before, add to existing score
                            for url in tags_json.subdict[term]:
                                #if url already grabbed, increment score by one
                                if url in urls:
                                    scores[urls.index(url)] += 1
                                else:
                                    #otherwise, add to list, give score of 1
                                    urls += [url]
                                    scores += [i/len(term)]
                                    caption_json = JsonGifs("Json/archivedcaptiongifs.json","global")
                                    max_tags += [len(caption_json.subdict[url][-1])]
                #get score
                for i in range(len(scores)):
                    scores[i] = scores[i]/max_tags[i]
                if len(urls) > 0:
                    #sort urls by score
                    scores, urls = zip(*sorted(zip(scores,urls),reverse=True))

                    #callback functions for previous button interaction
                    async def prev_gif_callback(interaction):
                        #get ID of search interaction
                        search_ID = interaction.data["custom_id"][:-1]
                        #get last search made by that user in discord scope
                        search_data = get_last_search(search_ID,str(interaction.guild_id),str(interaction.channel_id),str(interaction.user))
                        
                        #if no KeyError, and search_ID matches interaction
                        if search_data is not None and search_data["search_id"] == search_ID:

                            #get gifs, index from dictionary
                            gifs, i = search_data["gifs"], search_data["index"]
                            #decrement, wrapping around to len(urls) - 1 if < 0
                            i = i - 1 if i != 0 else len(urls) - 1

                            #edit embed with new description and url
                            embed.description = f"{i+1}/{len(urls)}"
                            embed.set_image(url=gifs[i])
                            embed.url = gifs[i]
                            #edit original message with new gif
                            await interaction.response.edit_message(embed=embed,view=view)
                            
                            #dump new values into json
                            last_search_json(str(search_ID),str(interaction.guild_id),str(interaction.channel_id),str(interaction.user),gifs,i)
                        else:
                            #otherwise defer interaction, only original user is allowed to interact with search
                            await interaction.response.defer()

                    #callback function for next button interaction
                    async def next_gif_callback(interaction):
                        #get ID of search interaction
                        search_ID = interaction.data["custom_id"][:-1]
                        #get last search made by that user in discord scope
                        search_data = get_last_search(search_ID,str(interaction.guild_id),str(interaction.channel_id),str(interaction.user))
                        
                        #if no KeyError, and search_ID matches interaction
                        if search_data is not None and search_data["search_id"] == search_ID:

                            #get gifs, index from dictionary
                            gifs, i = search_data["gifs"], search_data["index"]
                            #increment, wrapping around to 0 if > len(urls) - 1
                            i = (i + 1) % len(urls)

                            #edit embed with new description and url
                            embed.description = f"{i+1}/{len(urls)}"
                            embed.set_image(url=gifs[i])
                            embed.url = gifs[i]
                            #edit original message with new gif
                            await interaction.response.edit_message(embed=embed,view=view)
                            
                            #dump new values into json
                            last_search_json(str(search_ID),str(interaction.guild_id),str(interaction.channel_id),str(interaction.user),gifs,i)
                        else:
                            #otherwise defer interaction, only original user is allowed to interact with search
                            await interaction.response.defer()

                    async def delete_gif_callback(interaction):
                        await interaction.response.defer()

                    #define buttons
                    prev_button = Button(label='Previous Gif',style=discord.ButtonStyle.blurple)
                    next_button = Button(label='Next Gif',style=discord.ButtonStyle.blurple)
                    delete_button = Button(label='Delete Gif',style=discord.ButtonStyle.red)
                    view = View(prev_button,next_button,delete_button)

                    prev_button.custom_id = view.id + "0"
                    next_button.custom_id = view.id + "1"
                    delete_button.custom_id = view.id + "2"

                    prev_button.callback = prev_gif_callback
                    next_button.callback = next_gif_callback
                    delete_button.callback = delete_gif_callback

                    embed = Embed(
                        title = f"Search by {message.author}",
                        description=f"1/{len(urls)}",
                        colour = discord.Colour.blurple(),
                        url= urls[0],
                        type="link"
                    )
                    embed.set_image(url=urls[0])
                    embed.add_field(name="tags",value=str(original_search_terms)[1:-1].replace("'",""))

                    button_msg = await message.channel.send(embed=embed, view=view)

                    #store search made by that user in that channel in that server to json
                    last_search_json(str(view.id),str(message.guild.id),str(message.channel.id),str(message.author),urls,0)
                else:
                    await message.channel.send("sorry! no caption gifs with those tags can be found!")
            if msg[:8] == ".asearch":
                org_terms = msg[8:].replace(" ","").lower().split(",")
                search_terms = msg[8:].replace(" ","").lower().split(",")
                for i in range(len(search_terms)):
                    if search_terms[i][-1] != "s":
                        search_terms += [search_terms[i] + "s"]
                urls = []
                scores = []
                max_tags = []

                tags_json = JsonGifs("Json/tags.json","global")
                size = len(tags_json.subdict)
                start_time = timeit.default_timer()
                #for every search term the user inputted
                for term in search_terms:
                    #for every single slice of that search term
                    for i in range(len(term) + 1):
                        #if search term exists in tags
                        if tags_json.contains(term):
                            # yoink every url inside tag, if url has been grabbed before, add to existing score
                            for url in tags_json.subdict[term]:
                                #if url already grabbed, increment score by one
                                if url in urls:
                                    scores[urls.index(url)] += 1
                                else:
                                    #otherwise, add to list, give score of 1
                                    urls += [url]
                                    scores += [i/len(term)]
                                    caption_json = JsonGifs("Json/archivedcaptiongifs.json","global")
                                    max_tags += [len(caption_json.subdict[url][-1])]
                #sort urls by score
                #print(urls,scores)
                for i in range(len(scores)):
                    scores[i] = scores[i]/max_tags[i]
                if len(urls) > 0:
                    
                    await message.channel.send(f"{len(urls)} Gifs found! Just compiling (This may take up to 30 seconds)")
                    if len(urls) == 1:
                        await message.channel.send(f"{urls[0]}\nAfter only {round(timeit.default_timer() - start_time,0)} seconds, I searched through {size} tags and found this")#,file=discord.File("search.gif")
                        return
                    scores, urls = zip(*sorted(zip(scores,urls),reverse=True))
                    FONT_PATH = "Fonts/Futura Extra Black Condensed Regular.otf"
                    WIDTH = 1000
                    HEIGHT = 1000
                    #200,57,63 - red
                    #54,57,63 - discord
                    layout = Image.new("RGB",(WIDTH,HEIGHT),(54,57,63))

                    gifs = [Gif(urls[i],auto_download=True) for i in range(min(6,len(urls)))]
                    max_frames = min([len(gifs[i].frames) for i in range(len(gifs))])
                    result_frames = []
                    result_duration = [0] * max_frames

                    titleFont = ImageFont.truetype(FONT_PATH,80)
                    tagFont = ImageFont.truetype(FONT_PATH,40)
                    d = ImageDraw.Draw(layout)

                    #d.text((WIDTH//2,10),".Search",(255,255,255),titleFont,"mt")
                    d.text((WIDTH//2,10),str(org_terms),(255,255,255),tagFont,"mt")
                    if len(gifs) == 2:
                        NUM_HORZ = 2
                        NUM_VERT = 1
                    elif len(gifs) == 3 or len(gifs) == 4:
                        NUM_HORZ = 2
                        NUM_VERT = 2
                    elif len(gifs) == 5 or len(gifs) == 6:
                        NUM_HORZ = 3
                        NUM_VERT = 2
                    START_HEIGHT = 0
                    RES_HEIGHT = HEIGHT - START_HEIGHT
                    RES_WIDTH = WIDTH

                    #NUM_HORZ = 3
                    SIDE_HORZ_PADDING = (RES_HEIGHT * 0.2)/NUM_HORZ
                    INNER_HORZ_PADDING = (RES_HEIGHT * 0.1)/NUM_HORZ
                    
                    #NUM_VERT = 2
                    SIDE_VERT_PADDING = (RES_WIDTH * 0.15)/NUM_VERT
                    INNER_VERT_PADDING = (RES_WIDTH * 0.1)/NUM_VERT

                    BOX_WIDTH = round((RES_WIDTH - 2*SIDE_HORZ_PADDING - (NUM_HORZ - 1) * INNER_HORZ_PADDING)/NUM_HORZ)
                    BOX_HEIGHT = round((RES_HEIGHT - 2*SIDE_VERT_PADDING - (NUM_VERT - 1) * INNER_VERT_PADDING)/NUM_VERT)

                    box_pos = []
                    BOX_COUNT = NUM_HORZ * NUM_VERT
                    for row in range(NUM_HORZ):
                        for column in range(NUM_VERT):
                            #print(row,column)
                            TOP_LEFT_X = round(SIDE_HORZ_PADDING + (row * BOX_WIDTH) + ((row)*INNER_HORZ_PADDING))
                            TOP_LEFT_Y = round(START_HEIGHT + SIDE_VERT_PADDING + (column * BOX_HEIGHT) + ((column)*INNER_VERT_PADDING))
                            
                            BOT_RIGHT_X = round(TOP_LEFT_X + BOX_WIDTH)
                            BOT_RIGHT_Y = round(TOP_LEFT_Y + BOX_HEIGHT)
                            box_pos += [(TOP_LEFT_X,TOP_LEFT_Y,BOT_RIGHT_X,BOT_RIGHT_Y)]
                            #print(TOP_LEFT_X,TOP_LEFT_Y,BOT_RIGHT_X,BOT_RIGHT_Y)

                    for i in range(max_frames):
                        for box in range(len(gifs)):
                            rel_frame = (i % len(gifs[box].frames))
                            layout.paste(gifs[box].frames[rel_frame].resize((BOX_WIDTH,BOX_HEIGHT)),(box_pos[box]))
                            if i < len(gifs[box].frames):
                                result_duration[i] += gifs[box].durations[i]
                        result_frames += [copy(layout)]
                        result_duration[i] = result_duration[i]/len(gifs)

                    result = Gif(None,result_frames,result_duration)
                    #result_frames[0].save("search.gif", format="GIF",append_images=result_frames[1:],save_all=True,loop = 0, duration=[10 for i in range(len(result_frames))])
                    await resize_and_send(result,message)
                    await message.channel.send(f"After only {round(timeit.default_timer() - start_time,0)} seconds, I searched through {size} tags and found these top {len(gifs)} results!")#,file=discord.File("search.gif")
                    #os.remove("search.gif")
                else:
                    await message.channel.send("sorry! no caption gifs with those tags can be found!")
            if msg == ".decaption":
                await message.channel.send("decaptioning gif! give me a second to work!")
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    if gif.is_caption_gif():
                        gif.decaption()
                        await resize_and_send(gif, message)
                    else:
                        await message.channel.send("previous gif does not contain a caption")
                else:
                    await no_gif_found(message)
            if msg.split(" ")[0] == ".caption":
                text = message.content.split(" ", 1)[1]
                if text != "":
                    await message.channel.send("captioning gif! give me a second to work!")
                    gif = Gif(get_last(message),auto_download=True)
                    if gif.img != None:
                        gif.caption(text)
                        await resize_and_send(gif, message)
                    else:
                        await no_gif_found(message)
                else:
                    await message.channel.send("Please provide a caption!")
            if msg.split(" ")[0] == ".recaption":
                text = message.content.split(" ", 1)[1]
                if text != "":
                    await message.channel.send("recaptioning gif! give me a second to work!")
                    gif = Gif(get_last(message),auto_download=True)
                    if gif.img != None:
                        gif.decaption()
                        gif.caption(text)
                        await resize_and_send(gif, message)
                    else:
                        await no_gif_found(message)
            if msg.split(" ")[0] == ".speed":
                factor = float(msg.split(" ")[1])
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    await message.channel.send("speeding up gif!")
                    gif.change_speed(factor=factor)
                    await resize_and_send(gif, message)
                else:
                    await no_gif_found(message)
            if msg.split(" ")[0] == ".resize":
                factor = float(msg.split(" ")[1])
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    if gif.width * factor > 2500 or gif.height * factor > 2500:
                        await message.channel.send("you're going to break my fucking computer don't resize it this much")
                    else:
                        await message.channel.send("resizing gif!")
                        gif.resize(factor)
                        await resize_and_send(gif,message)
                else:
                    await no_gif_found(message)
            if msg == ".reverse":
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    await message.channel.send("reversing gif!")
                    gif.frames.reverse()
                    gif.durations.reverse()
                    await resize_and_send(gif,message)
                else:
                    await no_gif_found(message)
            if msg == ".stats":
                gif = Gif(get_last(message),auto_download=True)
                if gif.img != None:
                    stats = gif.stats()
                    await message.channel.send(f"Ratio: {stats[0]}\nMean: {stats[1]}\nMedian: {stats[2]}\nrms: {stats[3]}\nvar: {stats[4]}\nstd dev: {stats[5]}")  
                else:
                    await no_gif_found(message)
            if msg.split(" ")[0] == ".comgif":
                gif1 = Gif(get_last(message),auto_download=True)
                message.content = message.content.split(" ")[1]
                if gif_is_sent(message) != None:
                    dif = gif1.stats_dif(gif_is_sent(message))
                    same = gif1.is_same_gif(gif_is_sent(message))
                    await message.channel.send(f"Ratio Dif: {dif[0]}\nMean Dif: {dif[1]}\nMedian Dif (doesn't influence comp): {dif[2]}\nrms dif: {dif[3]}\nvar dif: {dif[4]}\nstd dev dif: {dif[5]}\nSame gif: {same}") 
                else:
                    await message.channel.send("link sent is not valid gif!")
            if msg.split(" ")[0] == ".sgif":
                gif1 = Gif(get_last(message),auto_download=True)
                message.content = message.content.split(" ")[1]
                if gif_is_sent(message) != None:
                    gif2 = Gif(gif_is_sent(message),auto_download=True)
                    # print(gif1.frames[0])
                    # print(gif2.frames[0])
                    if gif1.is_same_caption_gif(gif2):
                        await message.channel.send("These gifs are the same")
                    else:
                        await message.channel.send("These gifs are not the same")
                else:
                    await message.channel.send("link sent is not valid gif!")
            if msg == ".scrape":
                """
                scrapes all unique valid gif urls sent in channel 
                """
                start = timeit.default_timer()
                await message.channel.send("Attempting to scrape all unique gif urls from channel, this may take a while!")
                metadata = [message.guild.id,message.channel.id]
                channel = client.get_channel(message.channel.id)
                messages = await channel.history(limit=None,oldest_first = True).flatten()
                gif_urls = []
                for i in messages:
                    url = gif_is_sent(i)
                    if url != None and url not in gif_urls:
                        gif_urls += [[url] + metadata + [i.author.id]]
                with open(f"{message.channel.id}_scrape.txt","w") as f:
                    for i in gif_urls:
                        f.write(f"{i}\n")
                await message.channel.send(f"{len(gif_urls)} unique gif urls successfully scraped",file=discord.File(f"{message.channel.id}_scrape.txt"))
                os.remove(f"{message.channel.id}_scrape.txt")
                print(timeit.default_timer()-start)
            if msg == ".scrapeall":
                """
                scrapes all unique valid gif urls sent in server, while including attachment metadata
                """
                start = timeit.default_timer()
                await message.channel.send("Attempting to scrape all unique gif urls from server, this may take a while!")
                ids = [message.guild.text_channels[i].id for i in range(len(message.guild.text_channels))]
                gif_urls = []
                for channels in ids:
                    channel = client.get_channel(channels)
                    messages = await channel.history(limit=None,oldest_first = True).flatten()
                    for msg in messages:
                        url = gif_is_sent(msg)
                        if url != None and url not in gif_urls:
                            gif_urls += [[url,message.guild.id,channels,msg.author.id]]
                print(timeit.default_timer()-start)
                with open(f"{message.guild.id}_fullscrape.txt", "w") as f:
                    for i in gif_urls:
                        f.write(f"{i}\n")
                await message.channel.send(f"{len(gif_urls)} unique gif urls successfully scraped",file=discord.File(f"{message.guild.id}_fullscrape.txt"))
                os.remove(f"{message.guild.id}_fullscrape.txt")
            if msg ==".scrapeallx":
                """
                scrapes all unique valid gif urls sent in every server the bot is in (for my use only)
                """
                start = timeit.default_timer()
                await message.channel.send("Attempting to scrape all unique gif urls from all servers, this is literally going to take forever")
                text_channel_list = []
                for guild in client.guilds:
                    for channel in guild.text_channels:
                        text_channel_list += [channel.id]
                #print(text_channel_list)
                gif_urls = {}
                for channels in text_channel_list:
                    channel = client.get_channel(channels)
                    messages = await channel.history(limit=None,oldest_first = True).flatten()
                    for msg in messages:
                        url = gif_is_sent(msg)
                        if url != None and url not in gif_urls:
                            gif_urls[url] = 0
                print(timeit.default_timer()-start)
                with open("full_gif_scrape.txt", "w") as f:
                    for i in gif_urls:
                        f.write(f"{i}\n")
                await message.channel.send(f"{len(gif_urls)} unique gif urls successfully scraped",file=discord.File("full_gif_scrape.txt"))
                os.remove("full_gif_scrape.txt")
            if gif_is_sent(message) != None:
                #create URLAttachment Object containing url location data
                url = AttachmentURL(gif_is_sent(message),message.guild.id,message.channel.id,message.author.id)
                #update the last gif sent in the guild and channel in the JSON file
                last_gif_json(url)
                #instantiate gif object
                gif = Gif(url.url,auto_download=True)
                data = [url.guildID,url.channelID,url.userID]
                store_gif(url,gif,data)
        except Exception as e:
            await message.channel.send(f"{e}, Oops! Something went wrong!")
    
    client.run(TOKEN)
if __name__ == "__main__":
    # gifs = []
    # with open("taine_gifs.txt","r") as f:
    #     gifs = f.readlines()
    # guildID = "470896999722516480"
    # channelID = "712243005519560736"
    # userID = "158878635766317056"

    # failed_gifs = []
    # for i in range(1063,len(gifs)):
    #     try:
    #         ^
    #         url = AttachmentURL(gifs[i].strip(),guildID,channelID,userID)
    #         #instantiate gif object
    #         gif = Gif(url.url,auto_download=True)
    #         if gif._get_image(gif.img_reference):
    #             data = [url.guildID,url.channelID,url.userID]
    #             #if gif is a caption gif
    #             if gif.is_caption_gif():
    #                 caption = gif.text_from_caption() #get caption
    #                 tags = Tagger(caption).tags #get tags
    #                 data += [tags]
    #                 #await message.channel.send(tags)
    #                 tags_json = JsonGifs("Json/tags.json")
    #                 for tag in tags:
    #                     tags_json.set_catagory('global')
    #                     tags_json.addsubKey(tag)
    #                     if not tags_json.contains_alt_url(url,subkey=tag):
    #                         tags_json.add(url.url,data[:-1],tag)
    #                     tags_json.set_catagory('guild')
    #                     tags_json.addsubKey(url.guildID)
    #                     tags_json.addsubsubKey(url.guildID,tag)
    #                     if not tags_json.contains_alt_url(url,url.guildID,tag):
    #                         tags_json.add(url.url,data[:-1],url.guildID,tag)
    #                     tags_json.set_catagory('user')
    #                     tags_json.addsubKey(url.userID)
    #                     tags_json.addsubsubKey(url.userID,tag)
    #                     if not tags_json.contains_alt_url(url,url.userID,tag):
    #                         tags_json.add(url.url,data[:-1],url.userID,tag)
    #                 tags_json.dump_json()

    #             #instantiate json archiving object, file open depends on whether gif contains a caption
    #             archives = JsonGifs("Json/archivedcaptiongifs.json" if gif.is_caption_gif() else "Json/archivedgifs.json","global")
    #             if not archives.contains_alt_url(url):
    #                 archives.add(url.url,data) #add url to global key
    #             #print(archives.contains_alt_url(url))
    #             archives.set_catagory("guild") #set catagory to guild key
                
    #             archives.addsubKey(url.guildID) #if server ID not in guild key, add, then add url to server ID
    #             if not archives.contains_alt_url(url,url.guildID):
    #                 archives.add(url.url,None,url.guildID)
    #             #print(archives.contains_alt_url(url,url.guildID))
    #             archives.set_catagory("user") #if user ID not in user key, add, then add url to user ID
                
    #             archives.addsubKey(url.userID)
    #             if not archives.contains_alt_url(url,url.userID):
    #                 archives.add(url.url,None,url.userID)
    #             #print(archives.contains_alt_url(url,url.userID))
    #             archives.dump_json() #save json file
    #     except:
    #         print(gifs[i])
    #         failed_gifs += [gifs[i]]
    # else:
    #     print(gifs[i])
    #     failed_gifs += [gifs[i]]
    with open('C:/Users/maxcr/Desktop/Executables/giffytoken.txt') as f:
        TOKEN = f.readline()
    run_bot(TOKEN)
    #https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=36768320&scope=bot
    #https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=8&scope=bot
    #https://discordpy.readthedocs.io/en/stable/api.html#