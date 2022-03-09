import re

def extract(source_file,desination_file):
    file = open(source_file,"r")
    contents = file.read()
    print (contents)

    pattern = re.compile(r'"url":"(.*?)"')
    #this is the key save method

    #pattern = re.compile(r'url: "(.*?)"')
    #this is the log save method
    print (pattern)
    urls = pattern.finditer(contents)

    wfile = open(desination_file,"w")
    first = True
    #urlCount = 0
    for url in urls:
        #print (url.group(1))
        if first == True:
            wfile.write(url.group(1))
            first = False
            #urlCount += 1
        else:
            wfile.write("\n" + url.group(1))
            #urlCount += 1

    #print (urlCount)    
    wfile.close()
    file.close()

def prefix_gif():
    file = open("tonigif.txt")
    unique = []
    for url in file:
        prefix = url[8:].split('/',1)[0]
        if prefix not in unique:
            unique += [prefix]
    return unique
        
if __name__ == "__main__":
    extract("All gifs/alexgif.txt","alex.txt")
    #extract("max_gif_raw.txt","maxgifs.txt")
    #extract("taine_gif_raw.txt","tainegifs.txt")