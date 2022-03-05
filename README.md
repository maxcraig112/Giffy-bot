# Giffy-Bot
A multipurpose repos designed to allow the de-captioning and tagging of gifs, as well as other functionality to do with the catagorising, archiving and searching of gifs.

The repos provides abstraction of these commands through the discord bot Giffy


## Current list of Bot Commands
### Image Manipulation Commands
| Command  | Description |
| ------------- | ------------- |
| .caption [caption] | Content Cell  |
| .decaption | Content Cell  |
| .recaption [caption] | Content Cell  |
| .reverse  | Content Cell  |
| .speed  | Content Cell  |
| .resize [factor] | Content Cell  |

### Image Statistics
| Command  | Description |
| ------------- | ------------- |
| .cgif  | Content Cell  |
| .text  | Content Cell  |
| .tags  | Content Cell  |
| .stats  | Content Cell  |
| .comgif [gif]  | Content Cell  |
| .sgif [gif]  | Content Cell  |

### Gif Searching
| Command  | Description |
| ------------- | ------------- |
| .search [tag1,tag2,...]  | Content Cell  |
| .asearch [tag1,tag2,...]  | Content Cell  |

### Gif Retrieval
| Command  | Description |
| ------------- | ------------- |
| .lgif  | Content Cell  |
| .rgif  | Content Cell  |
| .rcgif  | Content Cell  |

### Gif Scraping
| Command  | Description |
| ------------- | ------------- |
| .scrape  | Content Cell  |
| .scrapeall  | Content Cell  |
| .scrapeallx  | Content Cell  |

### Debugging Tool
| Command  | Description |
| ------------- | ------------- |
| .test  | Content Cell  |

Aims of the bot
- Scraping caption gifs off tenor using API
- the user is able to enter a sentence to be used in a caption gif and the program can return an appropriate captionless gif to use
    - This could be achieved by analysing each word in the sentence, seperating it into nouns, adjectives, verbs. Then using those as search queries
    - Somehow scraping a large list of caption gifs, analysing the words they contain, grouping them together under similar subjects, and then using either a Neural Network or some   math to find the correct gif (certain words could link to gifs with a higher average red colour etc.) 

USE NLTK FOR WORD PROCESSING
CHECK THAT PIXEL 0,0 OF FIRST AND SECOND FRAME REMAINS CONSTANT

# DONE:
- Move json files to folder (DONE)
- work out fix for duplicate gifs being archived (DONE)
- method for taking list of gifs and archiving (DONE)
- improve captioning for large and small gifs, large and small text (DONE)
- give option to auto-download Gif when object instantiated (DONE)
- save gifs with names depending on channel and server sent so errors don't occur (DONE)
- gif captions sometimes flicker (DONE)
- "[WinError 32] The process cannot access the file because it is being used by another process" error when deleting temp files from server other than test_server (DONE)
- method for downloading all archived gifs (DONE)
- convert all cnd.discordapp.com to media.discordapp.net urls in json (DONE)
- fix tagging system so that more words are included (a lot of tags in the dictionary isn't that bad since O(1) complexity) (DONE)
- bot can now compare text of 2 caption gifs and return whether they are 80% the same sequence (DONE)
- bot can return whether or not it thinks 2 gifs are the same (caption and all) (DONE)
- increased __init__ robustness by allowing url,PIL object and Gif Object instantiation

# TODO:
- fix problems where it thinks certain white caption gifs are gifs, and where it thinks some caption gifs aren't gifs
- implement search by user,guild,global, maybe in class?
- interface for searching gifs and getting result
- create actual method for taking list of gifs
- maybe make it so the order of search terms searched influences the score?
- reprocess all gifs again to include more metadata
- add functionality to select a gif from asearch to be sent fully to chat
- add functionality which allows multiple pages of search
- add functionality to allow gifs to be removed from database from search (if they're just bad or wrong)
- Add better try,except code that's more robust for errors
- create small thumbnails of gifs when storing in archives
- if bot is captioning gif, automatically add to json with text inputted
    - create just stopwords for tags, keep all other words that are english
- potentially make it so giffy can caption MP4, jpeg,png as well
- refine stop_words list so that some words aren't removed
- if .rgif or .rcgif are used, don't try and process those gifs
- program for scraping urls from a channel using channel.history

# TODO BEFORE MASS REPROCESSESSING
- made it such that global tags hold data for all servers and users that have sent a gif
- actually figure out a robust way to find the caption of white gifs, and every gif 


 - https://discordpy-message-components.readthedocs.io/en/latest/
 - https://pypi.org/project/discord.py-message-components/
 - https://pypi.org/project/discord-components/
 - https://stackoverflow.com/questions/67722188/add-button-components-to-a-message-discord-py



# HOW TO MAKE BUTTON INTERACTIONS
- everytime you search in a channel, store that message result interaction ID in a json, similar to last gif
- when interaction is triggered, pull that ID with the list of gif results stored and increment
- only allowed 1 per channel?? just to avoid clogging up everything
- only person who searches can interact with buttons?