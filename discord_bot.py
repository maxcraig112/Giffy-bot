import json
import os
import random
from re import M, search
from typing import Dict
from gif import Gif
from validators.url import url
import discord
import validators
from discord.ext import commands
from URLJson import *
import timeit
from copy import copy

def run_bot(TOKEN):

    client = commands.Bot(command_prefix=".")

    def get_last(message):
        #get the last gif which was posted into the server
            with open("Json/lastgif.json", "r") as f:
                dict = json.load(f)
                try:
                    gif = dict[str(message.guild.id)][str(message.channel.id)]
                    return gif
                except KeyError:
                    return None

    async def no_gif_found(message):
        await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")
    
    async def resize_and_send(gif, message):
        gif.save("temp.gif")
        while os.path.getsize("temp.gif") > 8000000:
            #await message.channel.send("Caption too big! resizing!")
            gif = Gif("temp.gif")
            gif.resize(0.5)
            gif.save("temp.gif")
        await message.channel.send(file=discord.File("temp.gif"))
        os.remove("temp.gif")

    def gif_is_sent(message):
        if len(message.attachments) > 0 and os.path.splitext(message.attachments[-1].filename)[-1] == ".gif": # validators.url(message.attachments[-1].url) and 
            return message.attachments[-1].url
        if validators.url(message.content) and (message.content[-4:] == ".gif" or "tenor" in message.content):
            return message.content
        return None

    def last_gif_json(url):
        f = open("Json/lastgif.json","r")
        dict = json.load(f)
        if url.guildID not in dict: #if json database does not have key for current server
            dict[url.guildID] = {}  #add current server to json database
        #add url to key of channel.id. whether or not it exists, it will be created or placed there
        dict[url.guildID][url.channelID] = url.url
        with open("Json/lastgif.json","w") as fw:
            json.dump(dict, fw, indent=4)
    @client.event
    async def on_ready():
        print("Bot is ready")

    @client.event
    async def on_message(message):
        msg = message.content.lower()
        try:
            # if msg == "vore":
            #     await message.channel.send("<@217233850101661697>referenced the forbidden word 'vore', breaking a streak of 0 hour, 0 minutes, and 0 seconds. I'll wait 30 minutes and 0 seconds before warning you for this word again." )
            if msg == ".test":
                await message.channel.send("hello\nhow\nare\nyou")
            if msg == ".cgif":
                gif = Gif(get_last(message))
                gif._get_image(gif.img_reference)
                if gif.img != None:
                    if gif.is_caption_gif():
                        await message.channel.send("The last gif has a caption")
                    else:
                        await message.channel.send("The last gif does not have a caption")
                else:
                    no_gif_found(message)
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
                # gif = random.choice(os.listdir("All gifs/downloaded_gifs"))
                # await message.channel.send(file=discord.File(f"All gifs/downloaded_gifs/{gif}"))
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
                gif = Gif(get_last(message))
                gif._get_image(gif.img_reference)
                if gif.img != None:
                    text = gif.text_from_caption()
                    if text != None:
                        await message.channel.send(text)
                    else:
                        await message.channel.send("no text found")
                else:
                    no_gif_found(message)
            if msg == ".tags":
                gif = Gif(get_last(message))
                gif._get_image(gif.img_reference)
                if gif.img != None:
                    text = gif.text_from_caption()
                    if text != None:
                        tags = Tagger(text).tags #get tags
                        await message.channel.send(tags)
                else:
                    no_gif_found(message)
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
                    no_gif_found(message)
            if msg[:7] == ".search":
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
                    scores, urls = zip(*sorted(zip(scores,urls),reverse=True))
                    #print(urls,scores)
                    txt = f"It took {int(timeit.default_timer() - start_time)} seconds to search through {size} tags, out of {len(urls)} results, here are the top {min(len(urls),6)} i found! "
                    for i in range(min(6,len(urls))):
                        #print 5 highest scoring gifs
                        txt += f"{urls[i]}\n"
                    #print(scores[:5])
                    await message.channel.send(txt[:-1])
                    u = AttachmentURL(urls[min(len(urls)-1,4)],message.guild.id,message.channel.id,message.author.id)
                    last_gif_json(u)
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

                    gifs = [Gif(urls[i]) for i in range(min(6,len(urls)))]
                    for i in range(len(gifs)):
                        gifs[i]._get_image(gifs[i].img_reference)
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
                gif = Gif(get_last(message))
                gif._get_image(gif.img_reference)
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
                    gif = Gif(get_last(message))
                    gif._get_image(gif.img_reference)
                    if gif.img != None:
                        gif.caption(text)
                        await resize_and_send(gif, message)
                    else:
                        no_gif_found(message)
                else:
                    await message.channel.send("Please provide a caption!")
            if msg.split(" ")[0] == ".recaption":
                text = message.content.split(" ", 1)[1]
                if text != "":
                    await message.channel.send("recaptioning gif! give me a second to work!")
                    gif = Gif(get_last(message))
                    gif._get_image(gif.img_reference)
                    if gif.img != None:
                        gif.decaption()
                        gif.caption(text)
                        await resize_and_send(gif, message)
                    else:
                        no_gif_found(message)
            if msg == ".speed":
                gif = Gif(get_last(message))
                gif._get_image(gif.img_reference)
                if gif.img != None:
                    await message.channel.send("speeding up gif!")
                    gif.change_speed()
                    await resize_and_send(gif, message)
                else:
                    no_gif_found(message)
            if gif_is_sent(message) != None:
                #create URLAttachment Object containing url location data
                url = AttachmentURL(gif_is_sent(message),message.guild.id,message.channel.id,message.author.id)
                #update the last gif sent in the guild and channel in the JSON file
                last_gif_json(url)
                #instantiate gif object
                gif = Gif(url.url)
                gif._get_image(gif.img_reference)
                data = [url.guildID,url.channelID,url.userID]
                #if gif is a caption gif
                if gif.is_caption_gif():
                    caption = gif.text_from_caption() #get caption
                    tags = Tagger(caption).tags #get tags
                    data += [tags]
                    #await message.channel.send(tags)

                    tags_json = JsonGifs("Json/tags.json")
                    for tag in tags:
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
    #         print(f"{i}/{len(gifs)}")
    #         url = AttachmentURL(gifs[i].strip(),guildID,channelID,userID)
    #         #instantiate gif object
    #         gif = Gif(url.url)
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
    
    TOKEN = "ODkzMjkzMDc0NDEzOTE2MjMw.YVZWAQ.ThvEfXAcwD36XF9uedCWydq8D-c"
    run_bot(TOKEN)
    #https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=8&scope=bot
    #https://discordpy.readthedocs.io/en/stable/api.html#