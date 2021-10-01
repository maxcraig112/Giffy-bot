from bs4 import *
from io import BytesIO, StringIO
import os
import validators
import uuid
from typing import Text
import requests
import urllib.request
import shutil
from PIL import Image
from PIL import GifImagePlugin
import numpy as np
from pytesseract import *
pytesseract.tesseract_cmd = 'C:/Users/maxcr/Desktop/Executables/Tesseract/tesseract.exe'

def get_image(image_path: str):
    """
    Takes any form of image path
    - url
    - directory path
    - tenor url
    And converts it into PIL Image Object
    """
    if type(image_path) is not str:
        #image_path must already be in Object form
        return image_path
    if validators.url(image_path):
        r = requests.get(image_path, stream=True)
        if "tenor" in image_path:
            soup = BeautifulSoup(r.content)
            res = soup.findAll('div' , class_="Gif")
            res = res[0].img['src']
            r = requests.get(res, stream=True)
        img = Image.open(BytesIO(r.content))
        #img.show()
    else:
        img = Image.open(image_path)
    return img
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
def get_boundary(img, background: tuple) -> tuple:
    size = img.size
    if(background[0] in range(220,256) and background[1] in range(220,256) and background[2] in range(220,256)):
        boundary = 0
        x = img.getpixel((0,boundary))
        while(boundary < size[1] and x == background):
            x = img.getpixel((0,boundary))
            boundary += 10
        if boundary >= size[1]:
            #return None
            boundary -= 10
        while(img.getpixel((0,boundary)) != background):
            boundary -= 1
        if boundary in range(int(size[1] * 0.95),size[1] + 1):
            #if caption takes up over 95% of the screen, gif most likely isn't a caption gif, but instead is just solid white background
            return None
        i = 0
        while i < size[0]:
            if (background[0] not in range(220,256) and background[1] not in range(220,256) and background[2] not in range(220,256)):
                #if there are any pixels at the bottom of the caption which are not the colour of the caption background
                #then the image must not be a caption gif
                return None
            i  += 10
        return (size[0],boundary)
    return None
def get_top_caption(img, save: bool = False, file_name: str = None, path: str = None):
    img = get_image(img)
    pix = img.convert('RGB')
    #size = img.size
    background = pix.getpixel((0,0))
    boundary = get_boundary(pix, background)
    if boundary is not None:
        caption = pix.crop((0,0,boundary[0],boundary[1]))
        if save:
            file_name = get_file_name(file_name,path, specific_format=".jpeg")
            # if file_name is None:
            #     file_name = str(uuid.uuid1())
            # if path is not None:
            #     file_name = path + "/" + file_name 
            caption.save(file_name)
            print(f"caption saved as {file_name}")
        return caption
    return None
def get_text_from_caption_gif(image_path: str):
    img = get_image(image_path)
    caption = get_top_caption(img)
    if caption is not None:
        return pytesseract.image_to_string(img.resize(tuple(4*x for x in img.size)))[:-2].replace("\n"," ")
    else:
        return "No caption found, text may not be accurate\n" + pytesseract.image_to_string(img).replace("\n"," ")
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
            # if file_name is None:
            #     file_name = str(uuid.uuid1())
            #     if "tenor" in url:
            #         file_name += 'tenor'
            # file_name += ".gif"
            # if path is not None:
            #     file_name = path + "/" + file_name
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
def crop_and_save(img,boundary: tuple,file_name: str = None, path:str = None):
    frames = []
    for i in range(0,img.n_frames):
        img.seek(i)
        frames += [img.crop(boundary)]
    file_name = get_file_name(file_name,path,specific_format=".gif")
    frames[0].save(file_name, format="GIF",append_images=frames[1:],save_all=True)
def de_caption_gif(img, file_name: str = None, path:str = None):
    img = get_image(img)
    # if type(img) is str:
    #     if validators.url(img):
    #         response = requests.get(img)
    #         if "tenor" in img:
    #             soup = BeautifulSoup(response.content)
    #             res = soup.findAll('div' , class_="Gif")
    #             res = res[0].img['src']
    #             response = requests.get(res)
    #         img = Image.open(BytesIO(response.content))
    #     else:
    #         img = Image.open(img)
    pix = img.convert('RGB')
    background = pix.getpixel((0,0))
    boundary = get_boundary(pix, background)
    if boundary is not None:
        crop_and_save(img,(0,boundary[1]+1,boundary[0],pix.size[1]), file_name, path)
        return True
    else:
        print("gif does not contain a caption")
        return False
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
    #TESSERACT FILE ADDRESS IS SPECIFIC TO USER, AS GITHUB IS SHIT

    #Code for downloading all gifs in FILE_NAME to folders
    #Just comment out get_top_caption & de_caption_gif if you don't need/want the edited original gifs saved
    #Also all gifs being saved are name by the increment they were in the list
    #If you want randomly generated file names, replace str(i) with None
    FILE_NAME = 'cleangif.txt'
    GIF_FOLDER = 'downloaded_gifs'
    CAPTION_FOLDER = 'captions'
    DECAPTION_FOLDER = 'decaptioned_memes'

    caption_count = 0
    non_caption = 0
    for gif in os.listdir('downloaded_gifs'):
        img = get_image(f"downloaded_gifs/{gif}")
        pix = img.convert('RGB')
        background = pix.getpixel((0,0))
        if get_boundary(img,background) is not None:
            caption_count += 1
        else:
            non_caption += 1
    
    print(f"Caption Count: {caption_count}\nNon_Caption Count: {non_caption}\nPercentage Caption Gif: {((caption_count)/(caption_count + non_caption))*100}")
            
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
            

    

