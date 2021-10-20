import json
import os
import random
from re import M
from typing import Dict
from gif import Gif
from validators.url import url
import discord
import validators
from discord.ext import commands
from URLJson import *

def run_bot(TOKEN):

    client = commands.Bot(command_prefix=".")

    def get_last(message):
        #get the last gif which was posted into the server
            with open("lastgif.json", "r") as f:
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
            await message.channel.send("Caption too big! resizing!")
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
        f = open("lastgif.json","r")
        dict = json.load(f)
        if url.guildID not in dict: #if json database does not have key for current server
            dict[url.guildID] = {}  #add current server to json database
        #add url to key of channel.id. whether or not it exists, it will be created or placed there
        dict[url.guildID][url.channelID] = url.url
        with open("lastgif.json","w") as fw:
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
                gif = random.choice(os.listdir("All gifs/downloaded_gifs"))
                await message.channel.send(file=discord.File(f"All gifs/downloaded_gifs/{gif}"))
            if msg == ".givetext":
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
            if msg == ".lastgif":
                gif = get_last(message)
                if gif != "" and gif != None:
                    await message.channel.send(gif)
                else:
                    no_gif_found(message)
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

                #if gif is a caption gif
                if gif.is_caption_gif():
                    caption = gif.text_from_caption() #get caption
                    tags = Tagger(caption).tags #get tags
                    await message.channel.send(tags)
                #instantiate json archiving object, file open depends on whether gif contains a caption
                archives = JsonGifs("archivedcaptiongifs.json" if gif.is_caption_gif() else "archivedgifs.json","global")
                archives.add(url.url,[url.guildID,url.channelID,url.userID]) #add url to global key
                archives.set_catagory("guild") #set catagory to guild key
                
                archives.addsubKey(url.guildID) #if server ID not in guild key, add, then add url to server ID
                archives.add(url.url,None,url.guildID)
                
                archives.set_catagory("user") #if user ID not in user key, add, then add url to user ID
                archives.addsubKey(url.userID)
                archives.add(url.url,None,url.userID)

                archives.dump_json() #save json file
        except Exception as e:
            await message.channel.send(f"{e}, Oops! Something went wrong!")
    
    client.run(TOKEN)
if __name__ == "__main__":
    TOKEN = "ODkzMjkzMDc0NDEzOTE2MjMw.YVZWAQ.ThvEfXAcwD36XF9uedCWydq8D-c"
    run_bot(TOKEN)
    #https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=8&scope=bot
    #https://discordpy.readthedocs.io/en/stable/api.html#