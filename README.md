# Giffy-Bot
A multipurpose repos designed to allow the manipulation, tagging, archiving and retrieval of gifs.

This repos provides abstraction of these commands through the discord bot Giffy.

**Invite Link**
https://discord.com/api/oauth2/authorize?client_id=893293074413916230&permissions=36768320&scope=bot

## Current list of Bot Commands
### Image Manipulation Commands
| Command  | Description |
| ------------- | ------------- |
| .caption [caption] | Captions last gif with text given  |
| .decaption | Removes caption from last gif, if last gif does not contain a caption, returns exception |
| .recaption [caption] | Removes caption from last gif, and captions gif with text given  |
| .reverse  | Reverses gif  |
| .speed [factor] | Increases speed of gif by factor  |
| .resize [factor] | Resizes gif by factor |

### Image Statistics
| Command  | Description |
| ------------- | ------------- |
| .cgif  | Returns whether or not the last gif was a caption gif  |
| .text  | Returns caption text of last gif  |
| .tags  | Returns generated tags of last gif  |
| .ttags [text] | Returns the generated tags from the inputted text  |
| .stats  | Returns stats of uncaptioned last gif  |
| .comgif [gif]  | Compares stats of last gif and given gif  |
| .sgif [gif]  | Returns whether or not the uncaptioned last gif and given gif are the same  |

### Gif Searching
| Command  | Description |
| ------------- | ------------- |
| .search [tag1,tag2,...]  | Searches json file, collating all gif urls under specified tags. Generates score from what proportion of each gif contains the tags, sorts from highest score, and returns via an embedded discord message.  |
| .asearch [tag1,tag2,...]  | The same searching function as .search, however generates a gif which collates all search results into tiles. SHOULD BE REMOVED, takes forever to generate gif and is not an appealing format.  |

### Gif Retrieval
| Command  | Description |
| ------------- | ------------- |
| .lgif  | Returns the last gif seen by bot (stored in lastgif.json file)  |
| .rgif  | Returns random gif in archivedgifs.json  |
| .rcgif  | Returns random caption gif in archivedcaptiongifs.json  |

### Gif Scraping
| Command  | Description |
| ------------- | ------------- |
| .scrape  | Scrapes all unique urls in given channel, returning a txt file with url, Guild_ID, Channel_ID, User_ID  |
| .scrapeall  | Scrapes all unique urls in given server, returning a txt file with url, Guild_ID, Channel_ID, User_ID  |
| .scrapeallx  | Scrapes all unique urls in all servers the bot is in, returning a txt file with url, Guild_ID, Channel_ID, User_ID. This program takes forever and should not be ran.  |

### Debugging Tool
| Command  | Description |
| ------------- | ------------- |
| .giffy  | A link to github and a general description of the bot  |
| .help  | A list of commands  |
| .test  | Debugging command used for an assortment of code  |

### Exception Handling
In the case of an error, an error message is sent to the channel in the format of 
"{error}, Oops! Something went wrong!" 

Future aims of the bot
- Scraping caption gifs off tenor using API
- the user is able to enter a sentence to be used in a caption gif and the program can return an appropriate captionless gif to use
    - This could be achieved by analysing each word in the sentence, seperating it into nouns, adjectives, verbs. Then using those as search queries
    - Somehow scraping a large list of caption gifs, analysing the words they contain, grouping them together under similar subjects, and then using either a Neural Network or some math to find the correct gif (certain words could link to gifs with a higher average red colour etc.) 

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
- program for scraping urls from a channel using channel.history
- interface for searching gifs and getting result
- create actual method for taking list of gifs
- reprocess all gifs again to include more metadata
- Add better try,except code that's more robust for errors
- Tenor gifs seen by giffy are converted into embed version before adding to archive
- resulting .speed, .resize, .reverse gifs are not added to json

# TODO:
- add embedding to all commands
- fix problems where it thinks certain white caption gifs are gifs, and where it thinks some caption gifs aren't gifs (IMPOSSIBLE)
- implement search by user,guild,global, maybe in class?
- add functionality to allow gifs to be removed from database from search (if they're just bad or wrong)
- create small thumbnails of gifs when storing in archives
- if bot is captioning gif, automatically add to json with text inputted
    - create just stopwords for tags, keep all other words that are english
- potentially make it so giffy can caption MP4, jpeg,png as well
- refine stop_words list so that some words aren't removed
- if .rgif or .rcgif are used, don't try and process those gifs

# More commands to add
- bounce (similar to instagrams boomarang editing)
- invert - inverts the entire gif
- freeze - stops auto-replay of the gif
- grey - converts image to grayscale
- add custom text to gifs which are not properly read
- add interaction via DM's