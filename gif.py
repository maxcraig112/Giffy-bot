from enum import auto
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

#from caption import get_top_caption
pytesseract.tesseract_cmd = 'C:/Users/maxcr/Desktop/Executables/Tesseract/tesseract.exe'
#pytesseract.tesseract_cmd = '/home/pi/Desktop/Tesseract/tesseract.exe'

#Search from all gifs
#Search from gif in server
#Search from gif from user

class Gif:

    def __init__(self, image_reference: str = None, frames = None, durations = None, auto_download = False) -> None:
        self.img_reference = image_reference
        self.img = None
        self.frames = frames
        self.durations = durations
        self.width = None
        self.height = None
        if auto_download:
            self._get_image(image_reference)

    def _get_image(self,img):
        """
        Takes any expected form of image path and converts it into PIL Image Object
        
        INPUT: String representing an image path of directory or url type
        OUTPUT: The original image path in PIL Image Object form
        """
        try:
            if type(img) != str:
                #image_path must already be in Object form
                return img
            if validators.url(img):
                #attempt to request url data
                r = requests.get(img, stream=True)
                #if url is from Tenor
                if "tenor" in img:
                    #use BS4 to find exact url from html
                    soup = BeautifulSoup(r.content, features="html.parser")
                    res = soup.findAll('div' , class_="Gif")
                    res = res[0].img['src']
                    # rerequest url from new link
                    r = requests.get(res, stream=True)
                # open returned byte data in PIL Image Object form
                img = Image.open(BytesIO(r.content))
            else:
                #otherwise img is a directory path
                img = Image.open(img)
        except:
            return None
        self.img = img
        self.frames = self._get_frames()
        self.durations = self._get_duration()
        self._update_size()
        return img

    def _get_file_name(self, file_name: str, path: str):
        res = ""
        if file_name is None:
            res = str(uuid.uuid1())
        else:
            res += file_name
        if path != None:
            res = path + "/" + res
        return res

    def _get_frames(self) -> list:
        """
        Takes as input a PIL Image Object and returns a list of all frames contained
        within the Image. If Image Object is not GIF, len(frames) == 1
        """
        self._get_image(self.img)
        frames = []
        for i in range(0,self.img.n_frames):
            self.img.seek(i)
            frames += [self.img.convert("RGBA")]
        self.frames = frames
        return frames

    def _get_duration(self) -> list:
        """
        Takes as input a PIL Image Object and returns a list of the duration of all
        frames within the Image
        """
        duration = []
        for i in range(len(self.frames)):
            duration += [self.frames[0].info["duration"]]
        self.durations = duration
        return duration

    def _update_size(self):
        self.width = self.frames[0].size[0]
        self.height = self.frames[0].size[1]

    def is_caption_gif(self) -> bool:
        """
        Gets the result of the get_boundary method, if the method returns a tuple,
        the Gif contains a caption, otherwise it doesn't
        """
        res = self.get_boundary()
        return res != None
    
    def get_boundary(self) -> tuple:
        """
        For an Image object which contains a caption, the method will return a tuple
        representing the box which contains the top caption.
        
        If the Image object does not contain a caption, the method will return None

        Program currently considers the colour of the pixels 5 off from the left side
        This is to prevent small white bars from impacting the boundary finding
        If constant offset becomes a problem, could change it to 5% of the gif width.

        uses the 2nd frame of the Image as a method for determining if it contains
        a caption, this is because the 1st frame may be completely white, skewing results.

        """
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        if self.img != None:
            image = self.frames[1]
            background = image.getpixel((5,0))
            rang = range(220,256)
            if(background[0] in rang and background[1] in rang and background[2] in rang and background[3] != 0):
                boundary = 0
                x = image.getpixel((5,boundary))
                while(boundary < self.height and x == background):
                    x = image.getpixel((5,boundary))
                    boundary += 10
                if boundary >= self.height:
                    #return None
                    boundary -= 10
                while(image.getpixel((5,boundary)) != background):
                    boundary -= 1
                if boundary in range(int(self.height * 0.95),self.height + 1):
                    #if caption takes up over 95% of the screen, gif most likely isn't a caption gif, but instead is just solid white background
                    return None
                i = 0
                while i < self.width:
                    x = image.getpixel((i,boundary - 1))
                    if (x[0] not in rang and x[1] not in rang and x[2] not in rang):
                        #if there are any pixels at the bottom of the caption which are not the colour of the caption background
                        #then the image must not be a caption gif
                        return None
                    i  += 10
                return (self.width,boundary + 1)

    def get_top_caption(self):
        """
        returns an Image object which contains the cropped caption of the object.
        regardless of whether the Object is a gif or png/jpeg, the resulting Image
        Object will only be one frame

        Will return None if gif does not contain a caption
        """
        boundary = self.get_boundary()
        if boundary != None:
            caption = self.frames[1].crop((0,0,boundary[0],boundary[1]))
            return caption
        return None
    
    def get_uncaptioned_gif(self):
        boundary = self.get_boundary()
        if boundary != None:
            uncaption = self.frames[1].crop((0,boundary[1],self.width,self.height))
            return uncaption
        return self.frames[1]
    def text_from_caption(self) -> str:
        if self.img != None:
            caption = self.get_top_caption()
            if caption != None and caption != "":
                img = Image.new("RGBA",[caption.size[0]*2,caption.size[1]*2])
                img.paste(caption,(0,0))
                #print(pytesseract.image_to_string(caption))
                #pytesseract.image_to_string(caption.resize(tuple(4*x for x in caption.size)))
                return pytesseract.image_to_string(img.resize(tuple(4*x for x in caption.size)))[:-2].replace("\n"," ")
            else:
                return None
    
    def _crop(self, boundary: tuple,):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        for i in range(len(self.frames)):
            self.frames[i] = self.frames[i].crop(boundary)
            self._update_size()
    
    def decaption(self):
        boundary = self.get_boundary()
        if boundary != None:
            self._crop((0,boundary[1]+1,boundary[0],self.height))
            self._update_size()
        else:
            return None
    
    def caption(self, msg):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        factor = 1
        if self.width < 100:
            factor = math.ceil(400/self.width)
            self.resize(factor)
            self._update_size()
        
        FONT_PATH = "Fonts/Futura Extra Black Condensed Regular.otf"
        MIN_FONT_SIZE = 1
        MAX_FONT_SIZE = max(30,int(self.width/10))
        VERTICAL_PADDING = int(0.05 * self.height) #max(10,int(img.size[1]/25))
        HORIZONTAL_PADDING = int(0.05 * self.width)#max(10,int(img.size[0]/100))
        MAX_SIZE = self.width - 2 * HORIZONTAL_PADDING
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
        word_factor = 0.5
        while( (largest_word_size > MAX_SIZE and font_size >= MIN_FONT_SIZE) or largest_word_size > MAX_SIZE * word_factor):
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
        INNER_PADDING_FACTOR = 0.3
        LINE_HEIGHT = fnt.getsize(lines[0])[1]
        # the size of the caption space is equal to all the padding between lines, plus the height of all the combined lines
        #WHITE_BAR_SIZE = int((NUM_LINES + 1) * VERTICAL_PADDING + (NUM_LINES * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1]))
        WHITE_BAR_SIZE = int(2 * VERTICAL_PADDING + (NUM_LINES - 1) * LINE_HEIGHT * INNER_PADDING_FACTOR + (NUM_LINES * LINE_HEIGHT))

        text_caption = Image.new("RGBA",(self.width,WHITE_BAR_SIZE),(255,255,255))
        d = ImageDraw.Draw(text_caption)
        for i in range(NUM_LINES):
            #pos = (self.width//2,int((i + 1) * VERTICAL_PADDING + (i * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1])))
            pos = (self.width//2,int(VERTICAL_PADDING + i * LINE_HEIGHT * INNER_PADDING_FACTOR + (i * LINE_HEIGHT) + (LINE_HEIGHT/2)))
            d.text(pos,lines[i],(0,0,0),fnt,"mm",VERTICAL_PADDING)
        
        for k in range(len(self.frames)):
            new_frame = Image.new("RGBA",(self.width,WHITE_BAR_SIZE + self.height), color=(255,255,255))
            new_frame.paste(text_caption,(0,0))
            new_frame.paste(self.frames[k],(0,WHITE_BAR_SIZE))
            self.frames[k] = new_frame
            if factor != 1:
                self.frames[k].resize((int(self.width*factor**-1),int(self.height+WHITE_BAR_SIZE*factor**-1)))
        
        if factor != 1:
            self.resize(factor**-1)
        self._update_size()

    def change_speed(self, factor: float = 2, constant: int = None):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        for i in range(len(self.durations)):
            self.durations[i] = int(self.durations[i]/factor)
    
    def resize(self, factor: int):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        for i in range(len(self.frames)):
            self.frames[i] = self.frames[i].resize((int(self.width*factor),int(self.height*factor)))
        self._update_size()
    
    def reduce_frames(self, factor: float = 0.5):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        self.frames = [self.frames[i] for i in range(0,len(self.frames),int(1/factor))]

    def stats(self):
        """
        returns the mean, median and rms of a gif in uncaptioned form. Can be used for comparison of 2 gifs to see if they are the same. rounds values to 2 d.p
        """
        gif = self.get_uncaptioned_gif()
        #gif.show()
        ratio = [round(gif.size[0]/gif.size[1],2)]
        mean = [round(Stat(gif).mean[i],2) for i in range(3)]
        median = [round(Stat(gif).median[i],2) for i in range(3)]
        rms = [round(Stat(gif).rms[i],2) for i in range(3)]
        var = [round(Stat(gif).var[i],2) for i in range(3)]
        stddev = [round(Stat(gif).stddev[i],2) for i in range(3)]
        return [ratio,mean,median,rms,var,stddev]

    def stats_dif(self,img_reference):
        gif2 = Gif(img_reference,auto_download=True)
        if gif2 != None:
            stats1 = self.stats()
            stats2 = gif2.stats()
            if stats1[0][0] < stats2[0][0]:
                #swap around so that results are consistent
                stats1,stats2 = stats2, stats1
            dif = []
            ratio_dif = round(stats1[0][0]/stats2[0][0],2)
            # stats = [round(stats1[j][i]/stats2[j][i],2) for j in range(len(stats1)) for i in range(len(stats1[j]))]
            mean_dif = round(mean([round(stats1[1][i]/stats2[1][i],2) for i in range(3)]),2)
            median_dif = round(mean([round(stats1[2][i]/stats2[2][i],2) for i in range(3)]),2)
            rms_dif = round(mean([round(stats1[3][i]/stats2[3][i],2) for i in range(3)]),2)
            var_dif = round(mean([round(stats1[4][i]/stats2[4][i],2) for i in range(3)]),2)
            std_dif = round(mean([round(stats1[5][i]/stats2[5][i],2) for i in range(3)]),2)
            dif = [ratio_dif,mean_dif,median_dif,rms_dif,var_dif,std_dif]
            return dif
        else:
            #could not parse img_reference
            return None
    def same_gif(self,img_reference) -> bool:
        """
        compares the stats of the object and a 2nd gif and returns a boolean representing whether or not it thinks the uncaptioned gifs are the same
        """
        dif = self.stats_dif(img_reference)
        if dif != None:
            r = range(90,111)
            del dif[2]
            same = all([(dif[i]*100 in r) for i in range(len(dif))])
            return same
        else:
            #could not parse img_reference
            return None
    def save(self, file_name: str = None, path: str = None):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        file_name = self._get_file_name(file_name,path)
        self.frames[0].save(file_name, format="GIF",append_images=self.frames[1:],save_all=True,loop = 0, duration=self.durations)
    
    def show(self):
        if self.img is None:
            self.img = self._get_image(self.img_reference)
            
        self.img.show()

    def show_caption(self):
        if self.img is None:
            self.img = self._get_image(self.img_reference)

        boundary = self.get_boundary()
        if boundary is not None:
            self.get_top_caption().show()


if __name__ == "__main__":
    img = Gif("https://cdn.discordapp.com/attachments/712243005519560736/905742068381524038/712243005519560736_470896999722516480.gif")
    img.stats()
    