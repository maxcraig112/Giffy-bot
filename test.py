from PIL import Image, ImageDraw, ImageFont
from gif import Gif
import timeit
from copy import deepcopy, copy

if __name__ == "__main__":
    tags = ["joe","mama","gay","toni"]
    FONT_PATH = "Fonts/Futura Extra Black Condensed Regular.otf"
    WIDTH = 1000
    HEIGHT = 1000
    #200,57,63
    #54,57,63
    layout = Image.new("RGB",(WIDTH,HEIGHT),(54,57,63))
    url = ["https://cdn.discordapp.com/attachments/712243005519560736/900681564776710184/temp.gif",
"https://media.discordapp.net/attachments/841208671169675354/893832451741351986/caption.gif",
"https://media.discordapp.net/attachments/712243005519560736/900349123209887764/temp.gif",
"https://media.discordapp.net/attachments/712243005519560736/833315732477181972/freeze.gif",
"https://media.discordapp.net/attachments/712243005519560736/846924758259597362/caption.gif",
]

    gifs = [Gif(url[i]) for i in range(len(url))]
    start = timeit.default_timer()
    for i in range(len(gifs)):
        gifs[i]._get_image(gifs[i].img_reference)
    print(timeit.default_timer() - start)
    max_frames = min([len(gifs[i].frames) for i in range(len(gifs))])
    result_frames = []
    result_duration = [0] * max_frames

    titleFont = ImageFont.truetype(FONT_PATH,80)
    tagFont = ImageFont.truetype(FONT_PATH,40)
    d = ImageDraw.Draw(layout)

    #d.text((WIDTH//2,10),".Search",(255,255,255),titleFont,"mt")
    d.text((WIDTH//2,10),str(tags),(255,255,255),tagFont,"mt")
    START_HEIGHT = 0
    RES_HEIGHT = HEIGHT - START_HEIGHT
    RES_WIDTH = WIDTH

    NUM_HORZ = 3
    SIDE_HORZ_PADDING = (RES_HEIGHT * 0.2)/NUM_HORZ
    INNER_HORZ_PADDING = (RES_HEIGHT * 0.1)/NUM_HORZ
    
    NUM_VERT = 2
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

    result_frames[0].save("search.gif", format="GIF",append_images=result_frames[1:],save_all=True,loop = 0, duration=[10 for i in range(len(result_frames))])
