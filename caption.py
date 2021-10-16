from bs4 import *
from io import BytesIO, StringIO
import os
import validators
import uuid
from typing import Text
import requests
import urllib.request
from shutil import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
from pytesseract import *
pytesseract.tesseract_cmd = 'C:/Users/maxcr/Desktop/Executables/Tesseract/tesseract.exe'

def get_image(image_path: str):
    """
    Takes any form of image path and converts it into PIL Image Object
    - url
    - directory path
    - tenor url
    """
    try:
        if type(image_path) is not str:
            #image_path must already be in Object form
            return image_path
        if validators.url(image_path):
            r = requests.get(image_path, stream=True)
            if "tenor" in image_path:
                soup = BeautifulSoup(r.content, features="html.parser")
                res = soup.findAll('div' , class_="Gif")
                res = res[0].img['src']
                r = requests.get(res, stream=True)
            img = Image.open(BytesIO(r.content))
            #img.show()
        else:
            img = Image.open(image_path)
        return img
    except:
        print(f"could not open image {image_path}")
        return None
def get_file_name(file_name: str, path: str,file_type: bool = False, specific_format: str = None ):
    res = ""
    if file_name is None:
        res = str(uuid.uuid1())
    else:
        res += file_name
    if path is not None:
        res = path + "/" + res
    if file_type:
        res += os.path.splitext(file_name)[-1]
    elif specific_format is not None:
        res += specific_format
    return res
def get_boundary(img) -> tuple:
    """
    Program currently considers the colour of the pixels 5 off from the left side
    This is to prevent small white bars from impacting the boundary finding
    If constant offset becomes a problem, could change it to 5% of the gif width.
    """
    img = get_image(img)
    if img is not None:
        img = img.convert('RGBA')
        #size = img.size
        background = img.getpixel((5,0))
        size = img.size
        if(background[0] in range(220,256) and background[1] in range(220,256) and background[2] in range(220,256) and background[3] != 0):
            boundary = 0
            x = img.getpixel((0,boundary))
            while(boundary < size[1] and x == background):
                x = img.getpixel((5,boundary))
                boundary += 10
            if boundary >= size[1]:
                #return None
                boundary -= 10
            while(img.getpixel((5,boundary)) != background):
                boundary -= 1
            if boundary in range(int(size[1] * 0.95),size[1] + 1):
                #if caption takes up over 95% of the screen, gif most likely isn't a caption gif, but instead is just solid white background
                return None
            i = 0
            while i < size[0]:
                x = img.getpixel((i,boundary))
                if (x[0] not in range(220,256) and x[1] not in range(220,256) and x[2] not in range(220,256)):
                    #if there are any pixels at the bottom of the caption which are not the colour of the caption background
                    #then the image must not be a caption gif
                    return None
                i  += 10
            return (size[0],boundary + 1)
    return None
def get_top_caption(img, save: bool = False, file_name: str = None, path: str = None):
    boundary = get_boundary(img)
    pix = img.convert('RGBA')
    if boundary is not None:
        caption = pix.crop((0,0,boundary[0],boundary[1]))
        if save:
            file_name = get_file_name(file_name,path, specific_format=".jpeg") 
            caption.save(file_name)
            print(f"caption saved as {file_name}")
        return caption
    return None
def get_text_from_caption_gif(image_path: str):
    img = get_image(image_path)
    if img is not None:
        caption = get_top_caption(img)
        if caption is not None:
            return pytesseract.image_to_string(caption.resize(tuple(4*x for x in caption.size)))[:-2].replace("\n"," ")
        else:
            return "No caption found, text may not be accurate\n" + pytesseract.image_to_string(img).replace("\n"," ")
    return ""
def is_caption_gif(img) -> bool:
    res = get_boundary(img)
    return res is not None
def download_file(url: str, file_name: str = None, path: str = None) -> str:
    try:
        r = requests.get(url, stream=True)
        if "tenor" in url:
            soup = BeautifulSoup(r.content)
            res = soup.findAll('div' , class_="Gif")
            res = res[0].img['src']
            r = requests.get(res, stream=True)
        if r.status_code == 200:
            file_name = get_file_name(file_name, path,specific_format=".gif")
            with open(file_name, "wb") as out_file:
                shutil.copyfileobj(r.raw, out_file)
                #print(f"saved {url} as {file_name}")
            return file_name
        else:
            print(f"{url} could not be downloaded" )
            return None
    except:
        #try downloading using different method
        try:
            urllib.request.urlretrieve(url,file_name)
            return file_name
        except:
            pass
        print(f"{url} could not be downloaded" )
        return None
def get_frames(img,boundary: tuple = None) -> list:
    frames = []
    for i in range(0,img.n_frames):
        img.seek(i)
        if boundary is None:
            frames += [img.convert("RGBA")]
        else:
            frames += [img.crop(boundary).convert("RGBA")]
    return frames
def crop_and_save(img,boundary: tuple,file_name: str = None, path:str = None):
    frames = get_frames(img,boundary)
    file_name = get_file_name(file_name,path,specific_format=".gif")
    frames[0].save(file_name, format="GIF",append_images=frames[1:],save_all=True, loop=0)
def de_caption_gif(img, file_name: str = None, path:str = None):
    img = get_image(img)
    if img is not None:
        boundary = get_boundary(img)
        pix = img.convert('RGBA')
        if boundary is not None:
            crop_and_save(img,(0,boundary[1]+1,boundary[0],pix.size[1]), file_name, path)
            return True
        else:
            print("gif does not contain a caption")
            return False
    return None
def caption_gif(img, msg: str, file_name: str = None, path: str = None):
    img = get_image(img)
    # Variable Delcarations
    FONT_PATH = "Fonts/Futura Extra Black Condensed Regular.otf"
    MIN_FONT_SIZE = 1
    MAX_FONT_SIZE = max(30,int(img.size[0]/10))
    VERTICAL_PADDING = int(0.05 * img.size[1]) #max(10,int(img.size[1]/25))
    HORIZONTAL_PADDING = int(0.05 * img.size[0])#max(10,int(img.size[0]/100))
    WIDTH, HEIGHT = img.size
    MAX_SIZE = WIDTH - 2 * HORIZONTAL_PADDING
    font_size = MAX_FONT_SIZE

    # Declare font object
    comparisonFont = ImageFont.truetype(FONT_PATH, font_size)
    # Split message into individual words
    words = msg.split(" ")
    # Get width of all words within sentence
    word_size = [comparisonFont.getsize(words[i])[0] for i in range(len(words))]
    # largest word has the largest width
    largest_word = words[word_size.index(max(word_size))]
    # number of pixels of largest word
    largest_word_size = max(word_size)
    # keep on reducing size of font until largest word fits within text box, or minimum font size reached
    while(largest_word_size > MAX_SIZE and font_size >= MIN_FONT_SIZE):
        font_size -= 1
        largest_word_size = ImageFont.truetype(FONT_PATH, font_size).getsize(largest_word)[0]
    # instantiate font object with declared font size
    fnt = ImageFont.truetype(FONT_PATH, font_size)

    lines = []
    i = 0
    # while code hasn't added all words to a dedicated line
    while i < len(words):
        # declare new line
        line = words[i]
        # set index j to current word
        j = i
        # while adding another word still fits within the text box, and while we haven't ran out of words
        while j + 1 < len(words) and ImageFont.truetype(FONT_PATH, font_size).getsize(line + words[j+1] + " ")[0] <= MAX_SIZE:
            # go to next word
            j += 1
            # add word + space to line
            line += " " + words[j]
        # when can no longer fit more words, or ran out of words, add new line to list of lines
        lines += [line]
        # iterate i to next word that hasn't been assigned a line
        i = j + 1
    NUM_LINES = len(lines)
    # the size of the caption space is equal to all the padding between lines, plus the height of all the combined lines
    WHITE_BAR_SIZE = (NUM_LINES + 1) * VERTICAL_PADDING + (NUM_LINES * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1])
    # convert gif into frames
    frames = get_frames(img)
    # get duration of each frame of gif
    DURATION = []
    for i in range(len(frames)):
        DURATION += [frames[0].info['duration']]

    text_caption = Image.new("RGBA",(WIDTH,WHITE_BAR_SIZE),(255,255,255))
    d = ImageDraw.Draw(text_caption)
    for i in range(NUM_LINES):
        pos = (WIDTH//2,(i + 1) * VERTICAL_PADDING + (i * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1]))
        d.text(pos,lines[i],(0,0,0),fnt,"mt",VERTICAL_PADDING)
    
    for k in range(len(frames)):
        new_frame = Image.new("RGBA",(WIDTH,WHITE_BAR_SIZE + HEIGHT), color=(255,255,255))
        new_frame.paste(text_caption,(0,0))
        new_frame.paste(frames[k],(0,WHITE_BAR_SIZE))
        frames[k] = new_frame
    """
    for k in range(len(frames)):
        frames[k] = ImageOps.pad(frames[k], (WIDTH, HEIGHT + WHITE_BAR_SIZE), color=(255,255,255), centering=(0,1),method=Image.LANCZOS)
        d = ImageDraw.Draw(frames[k])
        for i in range(NUM_LINES):
            pos = (WIDTH//2,(i + 1) * VERTICAL_PADDING + (i * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1]))
            d.text(pos,lines[i],(0,0,0),fnt,"mt",VERTICAL_PADDING)
    #frames[0].show()
    """
    if file_name is None:
        file_name = get_file_name(None,path,".gif")
    frames[0].save(file_name, format="GIF",append_images=frames[1:],save_all=True,loop = 0, duration=DURATION)
def change_speed(img,speed_factor: float,constant: int = None, file_name: str = None, path: str = None):
    img = get_image(img)
    frames = get_frames(img)
    DURATION = []
    for i in range(len(frames)):
        if constant is not None:
            DURATION += [constant]
        else:
            DURATION += [int(frames[0].info['duration']/speed_factor)]
    if file_name is None:
        file_name = get_file_name(None,path,".gif")
    frames[0].save(file_name, format="GIF",append_images=frames[1:],save_all=True,loop = 0, duration=DURATION)
def resize_file(img,old_size: int, new_size: int, file_name: str = None, path: str = None):
    img = Image.open(img)
    frames = get_frames(img)
    new_scale = (new_size/old_size)**(1/2)
    size = img.size
    for i in range(len(frames)):
        frames[i] = frames[i].resize((int(size[0]*new_scale),int(size[1]*new_scale)))
    #img = img.resize((int(size[0]*new_scale),int(size[1]*new_scale)))
    file_name = get_file_name(file_name,path)
    frames[0].save(file_name, format="GIF",append_images=frames[1:],save_all=True,loop = 0)
    #img.save(file_name,save_all=True,format="GIF",loop=0)
def reduce_frames(img, reduction_factor: float = 0.5, file_name: str = None, path: str = None):
    img = get_image(img)
    frames = get_frames(img)
    file_name = get_file_name(file_name,path)
    frames = [frames[i] for i in range(0,len(frames),int(1/reduction_factor))]
    frames[0].save(file_name, format="GIF",append_images=frames[1:],save_all=True,loop = 0)
def read_file(file_name) -> list:
    lst = []
    try:
        with open(file_name) as f:
            for line in f:
                lst += [line.strip()]
    except FileNotFoundError:
        print(f"{file_name} does not exist")
    return lst
if __name__ == "__main__":
    # bible = ""
    # with open("bible.txt", "r") as f:
    #     bible = f.readlines()
    #     caption = ""
    #     for i in range(len(bible)):
    #         caption += bible[i] + " "
    #     caption = caption.replace("\n","")
    # print("reading bible done")
    # caption_gif("https://tenor.com/view/monday-typing-monkey-working-hard-funny-animals-type-writer-gif-12177139",caption,"the_holy_savour.gif")
    # img = Image.open('failed_gifs/58852138-227f-11ec-9f72-5cf370a080b0.gif')
    # img = img.convert("RGBA")
    # print(img.getpixel((0,0)))

    # #Code for getting all caption gifs from a folder of unfiltered gifs
    # #Used to test robustness of is_caption_gif function
    # for gif in os.listdir("downloaded_gifs"):
    #     if is_caption_gif(f"downloaded_gifs/{gif}"):
    #         copyfile(f"downloaded_gifs/{gif}",f"caption_gifs/{gif}")


    #TESSERACT FILE ADDRESS IS SPECIFIC TO USER, AS GITHUB IS SHIT

    #Code for downloading all gifs in FILE_NAME to folders
    #Just comment out get_top_caption & de_caption_gif if you don't need/want the edited original gifs saved
    #Also all gifs being saved are name by the increment they were in the list
    #If you want randomly generated file names, replace str(i) with None
    FILE_NAME = 'cleangif.txt'
    GIF_FOLDER = 'downloaded_gifs'
    CAPTION_FOLDER = 'captions'
    DECAPTION_FOLDER = 'decaptioned_memes'        
    """
    if not os.path.isdir(GIF_FOLDER):
        os.makedirs(GIF_FOLDER)
    if not os.path.isdir(CAPTION_FOLDER):
        os.makedirs(CAPTION_FOLDER)
    if not os.path.isdir(DECAPTION_FOLDER):
        os.makedirs(DECAPTION_FOLDER)
    urls = read_file(FILE_NAME)
    for i in range(len(urls)):
        path = download_file(urls[i],None,GIF_FOLDER)
        #if path is not None:
            #get_top_caption(path,True, str(i),CAPTION_FOLDER)
            #de_caption_gif(path, str(i),DECAPTION_FOLDER)
    """