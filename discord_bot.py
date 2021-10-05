import json
import os
import random
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

    @client.event
    async def on_ready():
        print("Bot is ready")

    @client.command()
    # async def getlast(message):
    #     #get the last gif which was posted into the server
    #     with open("gifs.json", "r") as f:
    #         dict = json.load(f)
    #         try:
    #             gif = dict[message.guild.id][message.channel.id]
    #             await message.channel.send(gif)
    #         except KeyError:
    #             await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was off when a gif was sent!")

    @client.event
    async def on_message(message):
        """
        #if message send is of bot, send nothing (otherwise inf loop)
        if message.author == client.user:
            return
        """
        if message.content.lower() == ".test":
            await message.channel.send("&caption i am a bot!")
        if message.content.lower() == ".help":
            await message.channel.send("**rgif**\n- randomly upload gif (gif cannot be used for other commands)\n**givetext** \n- returns the text contains on the last sent gif (works best with caption gifs, non-captions gifs may be inaccurate)\n**lastgif**\n- returns the last gif send to the channel (last gif sent when giffyBot was online)\n**decaption**\n- removes the top caption of the last send gif, does not alter non-caption gifs")
        if message.content.lower() == ".cgif":
            gif = get_last(message)
            if is_caption_gif(gif):
                await message.channel.send("The last gif has a caption")
            else:
                await message.channel.send("The last gif does not have a caption")
        if message.content.lower() == ".rgif":
            gif = random.choice(os.listdir("downloaded_gifs"))
            await message.channel.send(file=discord.File(f"downloaded_gifs/{gif}"))

        if message.content.lower() == ".givetext":
            gif = get_last(message)
            if gif is not None:
                text = get_text_from_caption_gif(gif)
                if text != "":
                    await message.channel.send(text)
                else:
                    await message.channel.send("no text found")
            else:
                await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")

        if message.content.lower() == ".lastgif":
            gif = get_last(message)
            if gif is not None:
                await message.channel.send(gif)
                return
            else:
                await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")

        if message.content.lower() == ".decaption":
            gif = get_last(message)
            if gif is not None:
                await message.channel.send("decaptioning gif! give me a second to work!")
                res = de_caption_gif(gif,"temp")
                if res:
                    if os.path.getsize("temp.gif") > 8000000:
                        reduction_factor = min(0.5,8000000/os.path.getsize("temp.gif"))
                        #await message.channel.send(f"caption gif was over discords file limit, so i reduced the frames by {100 - int(reduction_factor*100)}%")
                        reduce_frames(res,reduction_factor,"temp.gif")
                    await message.channel.send(file=discord.File("temp.gif"))
                    #remove temporary file after it's been send
                    os.remove("temp.gif")
                else:
                    await message.channel.send("previous gif does not contain a caption")
            else:
                await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")
        if message.content.lower().split(" ")[0] == ".caption":
            gif = get_last(message)
            if gif is not None:
                await message.channel.send("captioning gif! give me a second to work!")
                msg = message.content.split(" ", 1)[1]
                if msg != "":
                    caption_gif(gif,msg,"temp.gif")
                    if os.path.getsize("temp.gif") > 8000000:
                        reduction_factor = min(0.5,8000000/os.path.getsize("temp.gif"))
                        #await message.channel.send(f"caption gif was over discords file limit, so i reduced the frames by {100 - int(reduction_factor*100)}%")
                        reduce_frames("temp.gif",reduction_factor,"temp.gif")
                    await message.channel.send(file=discord.File("temp.gif"))
                    #remove temporary file after it's been send
                    os.remove("temp.gif")
                else:
                    await message.channel.send("Please provide a caption!")
            else:
                await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")
        if message.content.lower().split(" ")[0] == ".recaption":
            gif = get_last(message)
            if gif is not None:
                msg = message.content.split(" ", 1)[1]
                if msg != "":
                    await message.channel.send("recaptioning gif! give me a second to work!")
                    res = de_caption_gif(gif,"temp")
                    if res:
                        caption_gif("temp.gif",msg,"temp.gif")
                        if os.path.getsize("temp.gif") > 8000000:
                            reduction_factor = min(0.5,8000000/os.path.getsize("temp.gif"))
                            #await message.channel.send(f"caption gif was over discords file limit, so i reduced the frames by {100 - int(reduction_factor*100)}%")
                            reduce_frames("temp.gif",reduction_factor,"temp.gif")
                        await message.channel.send(file=discord.File("temp.gif"))
                        #remove temporary file after it's been send
                        os.remove("temp.gif")
                    else:
                        await message.channel.send("previous gif does not contain a caption")
                else:
                    await message.channel.send("Please provide a caption!")
                
            else:
                await message.channel.send("No previous gifs found in channel. This may be because I haven't been in the server long or I was offline when a gif was sent!")
        if len(message.attachments) > 0:
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
           f = open("gifs.json", "r")
           dict = json.load(f)
           if str(message.guild.id) not in dict: #if json database does not have key for current server
               dict[str(message.guild.id)] = {}  #add current server to json database
            #add url to key of channel.id. whether or not it exists, it will be created or placed there
           dict[str(message.guild.id)][str(message.channel.id)] = message.content
           f.close()
           with open("gifs.json","w") as fw:
               json.dump(dict, fw, indent=4)
    
    client.run(TOKEN)
if __name__ == "__main__":
    # with open("test.json", "w") as f:
    #     json.dump({"age": "17"},f,indent=4)
    TOKEN = "ODkzMjkzMDc0NDEzOTE2MjMw.YVZWAQ.ThvEfXAcwD36XF9uedCWydq8D-c"
    run_bot(TOKEN)
    #https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=8&scope=bot
    #https://discordpy.readthedocs.io/en/stable/api.html#