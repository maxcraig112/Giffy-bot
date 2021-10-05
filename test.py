from PIL import Image, ImageDraw, ImageFont, ImageOps

def get_frames(img,boundary: tuple = None) -> list:
    if boundary is None:
        boundary = (0,0,img.size[0],img.size[1])
    frames = []
    for i in range(0,img.n_frames):
        img.seek(i)
        frames += [img.crop(boundary).convert("RGB")]
    return frames

def caption_gif(img, msg):
    FONT_PATH = "Myriad Pro Bold.ttf"
    MIN_FONT_SIZE = 1
    MAX_FONT_SIZE = max(30,int(30 * img.size[0]/300))
    VERTICAL_PADDING = max(10,int(img.size[1]/25))
    HORIZONTAL_PADDING = max(10,int(img.size[0]/100))
    WIDTH, HEIGHT = img.size
    MAX_SIZE = WIDTH - 2 * HORIZONTAL_PADDING
    font_size = MAX_FONT_SIZE

    # get a font
    comparisonFont = ImageFont.truetype(FONT_PATH, font_size)
    words = msg.split(" ")
    word_size = [comparisonFont.getsize(words[i])[0] for i in range(len(words))] #Get width of all words within sentence
    largest_word = words[word_size.index(max(word_size))]
    largest_word_size = max(word_size)
    while(largest_word_size > MAX_SIZE and font_size >= MIN_FONT_SIZE):
        font_size -= 1
        largest_word_size = ImageFont.truetype(FONT_PATH, font_size).getsize(largest_word)[0]
    fnt = ImageFont.truetype(FONT_PATH, font_size)

    lines = []
    i = 0
    while i < len(words):
        line = words[i]
        j = i
        while j + 1 < len(words) and ImageFont.truetype(FONT_PATH, font_size).getsize(line + words[j+1] + " ")[0] <= MAX_SIZE:
            j += 1
            line += " " + words[j]
        lines += [line]
        i = j + 1
    print(lines)
    NUM_LINES = len(lines)
    WHITE_BAR_SIZE = (NUM_LINES + 1) * VERTICAL_PADDING + (NUM_LINES * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1])
    frames = get_frames(img)

    for i in range(len(frames)):
        frames[i] = ImageOps.pad(frames[i], (WIDTH, HEIGHT + WHITE_BAR_SIZE), color=(255,255,255), centering=(0,1),method=Image.LANCZOS)
        # result = Image.new(frames[i].mode, (WIDTH, HEIGHT + WHITE_BAR_SIZE), (0,255,255))
        # result.paste(frames[i], (0, WHITE_BAR_SIZE))
        # #result.show()
        # frames[i] = result
        d = ImageDraw.Draw(frames[i])
        for i in range(NUM_LINES):
            pos = (WIDTH//2,(i + 1) * VERTICAL_PADDING + (i * ImageFont.truetype(FONT_PATH, font_size).getsize(lines[0])[1]))
            d.text(pos,lines[i],(0,0,0),fnt,"mt",VERTICAL_PADDING)
    #img = ImageOps.pad(img, (WIDTH, HEIGHT + WHITE_BAR_SIZE), color=(255,255,255), centering=(0,1))
    #img.show()
    # for i in range(len(frames)):
    #     frames[i].show()
    # print(frames[0].format)
    frames[0].save("test1.gif", format="GIF",append_images=frames[1:],save_all=True)
        

    # get a drawing context
    
    # draw multiline text
    # print(font_size)
    # d.text((img.size[0]//2,0), msg, font=fnt, fill=(0, 0, 0), align="center",anchor="mt")
    # print(d.textsize("Hello", font=fnt))
    # img.show()
if __name__ == "__main__":
    #img = Image.new("RGB", (300, 500), (240, 240, 240))
    img = Image.open("failed_gifs/4e36a772-227b-11ec-95e9-5cf370a080b0.gif")
    #img = Image.open("troll.gif")
    #img = Image.open("t1.png")
    #img.show()
    msg = "we do a little captioning"
    caption_gif(img,msg)
