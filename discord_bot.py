import json
import os
import random
from re import M
from typing import Dict
from gif import Gif
from validators.url import url
from caption import *
import discord
import validators
from discord.ext import commands

def run_bot(TOKEN):

    client = commands.Bot(command_prefix=".")

    def get_last(message):
        #get the last gif which was posted into the server
            with open("gifs.json", "r") as f:
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
            gif.resize(0.75)
            gif.save("temp.gif")
        await message.channel.send(file=discord.File("temp.gif"))
        os.remove("temp.gif")

    @client.event
    async def on_ready():
        print("Bot is ready")

    @client.event
    async def on_message(message):
        msg = message.content.lower()
        try:
            if msg == ".cgif":
                gif = Gif(get_last(message))
                if gif.img is not None:
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
                if gif.img is not None:
                    text = gif.text_from_caption()
                    if text is not None:
                        await message.channel.send(text)
                    else:
                        await message.channel.send("no text found")
                else:
                    no_gif_found(message)
            if msg == ".lastgif":
                gif = get_last(message)
                if gif.img is not None:
                    await message.channel.send(gif)
                else:
                    no_gif_found(message)
            if msg == ".decaption":
                gif = Gif(get_last(message))
                if gif.img is not None:
                    await message.channel.send("decaptioning gif! give me a second to work!")
                    if gif.is_caption_gif:
                        gif.decaption()
                        resize_and_send(gif, message)
                    else:
                        await message.channel.send("previous gif does not contain a caption")
                else:
                    no_gif_found(message)
            if msg.split(" ")[0] == ".caption":
                gif = Gif(get_last(message))
                if gif.img is not None:
                    await message.channel.send("captioning gif! give me a second to work!")
                    text = message.content.split(" ", 1)[1]
                    if text != "":
                        gif.caption(text)
                        resize_and_send(gif, message)
                    else:
                        await message.channel.send("Please provide a caption!")
                else:
                    no_gif_found(message)
            if msg.split(" ")[0] == ".recaption":
                gif = Gif(get_last(message))
                if gif.img is not None:
                    msg = message.content.split(" ", 1)[1]
                    if msg != "":
                        await message.channel.send("recaptioning gif! give me a second to work!")
                        gif.decaption()
                        gif.caption(text)
                        resize_and_send(gif, message)
                    else:
                        await message.channel.send("Please provide a caption!")

                else:
                    no_gif_found(message)
            if msg == ".speed":
                gif = Gif(get_last(message))
                if gif.img is not None:
                    await message.channel.send("speeding up gif!")
                    gif.change_speed()
                    resize_and_send(gif, message)
                else:
                    no_gif_found(message)
            if len(message.attachments) > 0:
                # if message.attachments[-1][-4:] == ".gif" or "tenor" in message.content:
                x = message.attachments[-1].url
                if validators.url(x):
                    #if the user has send an attachment, the last attachment send will be added to json
                    f = open("gifs.json", "r")
                    dict = json.load(f)
                    if str(message.guild.id) not in dict: #if json database does not have key for current server
                        dict[str(message.guild.id)] = {}  #add current server to json database
                    #add url to key of channel.id. whether or not it exists, it will be created or placed there
                    dict[str(message.guild.id)][str(message.channel.id)] = str(message.attachments[-1])
                    f.close()
                    with open("gifs.json","w") as fw:
                        json.dump(dict, fw, indent=4)
            
            #if the message send in chat is a url (very buggy, lets assume that all urls are pictures)
            if validators.url(message.content):
                if message.content[-4:] == ".gif" or "tenor" in message.content:
                    f = open("gifs.json", "r")
                    dict = json.load(f)
                    if str(message.guild.id) not in dict: #if json database does not have key for current server
                        dict[str(message.guild.id)] = {}  #add current server to json database
                        #add url to key of channel.id. whether or not it exists, it will be created or placed there
                    dict[str(message.guild.id)][str(message.channel.id)] = message.content
                    f.close()
                    with open("gifs.json","w") as fw:
                        json.dump(dict, fw, indent=4)
        except Exception as e:
            await message.channel.send(f"{e}, Oops! Something went wrong!")
    
    client.run(TOKEN)
if __name__ == "__main__":
    TOKEN = "ODkzMjkzMDc0NDEzOTE2MjMw.YVZWAQ.ThvEfXAcwD36XF9uedCWydq8D-c"
    run_bot(TOKEN)
    #https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=8&scope=bot
    #https://discordpy.readthedocs.io/en/stable/api.html#