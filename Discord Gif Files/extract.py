import re

def extract():
    file = open("message_17.txt","r")
    contents = file.read()
    print (contents)

    pattern = re.compile(r'"url":"(.*?)"')
    #this is the key save method

    #pattern = re.compile(r'url: "(.*?)"')
    #this is the log save method
    print (pattern)
    urls = pattern.finditer(contents)

    wfile = open("taine_gifs.txt","w")
    first = True
    #urlCount = 0
    for url in urls:
        print (url.group(1))
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
    extract()