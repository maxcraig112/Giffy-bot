from PIL import Image


if __name__ == "__main__":
    WIDTH = 100
    HEIGHT = 100
    img = Image.new("RGB",(WIDTH,HEIGHT),(255,255,255))
    img2 = Image.new("RGB",(10,10),(0,0,0))
    duration = [10,10]
    pixels = img.load()
    #
    for i in range(HEIGHT):
        for j in range(WIDTH):
            pixels[i,j] = (i+j,i+j,i+j)
    #pixels[0,0] = (255,0,0)

    #self.frames[0].save(file_name, format="GIF",append_images=self.frames[1:],save_all=True,loop = 0, duration=self.durations)
    img.save("large.gif",format="GIF",save_all=True,loop=0,duration=duration)