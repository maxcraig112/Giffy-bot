# Giffy-Bot
A mutlipurpose repos designed to allow the de-captioning and tagging of gifs, as well as other functionality to do with the catagorising, archiving and searching of gifs.

The repos provides abstraction of these commands through the discord bot Giffy


Current list of Bot Commands
- decaption a caption gif
- return text in a gif
- store last gif posted to server
- create caption gifs
- store all unique gifs sent 
    - Globally
    - in each guild
    - by each user
- Tags all caption gifs according to the
    - Nouns
    - Adjectives
    - Verbs
- contained within their caption
- Allows the searching of gifs through these tags

Aims of the bot
- Scraping caption gifs off tenor using API
- the user is able to enter a sentence to be used in a caption gif and the program can return an appropriate captionless gif to use
    - This could be achieved by analysing each word in the sentence, seperating it into nouns, adjectives, verbs. Then using those as search queries
    - Somehow scraping a large list of caption gifs, analysing the words they contain, grouping them together under similar subjects, and then using either a Neural Network or some   math to find the correct gif (certain words could link to gifs with a higher average red colour etc.) 

USE NLTK FOR WORD PROCESSING
CHECK THAT PIXEL 0,0 OF FIRST AND SECOND FRAME REMAINS CONSTANT

DONE:
- Move json files to folder (DONE)
- work out fix for duplicate gifs being archived (DONE)
- method for taking list of gifs and archiving (DONE)
TODO:
- improve captioning for large and small gifs, large and small text
- fix problems where it thinks certain white caption gifs are gifs, and where it thinks some caption gifs aren't gifs
- implement search by user,guild,global, maybe in class?
- interface for searching gifs and getting result
- create actual method for taking list of gifs
- method for downloading all archived gifs, reprocesssing them
- maybe make it so the order of search terms searched influences the score?
- reprocess all gifs so that full text is included too
- add functionality to select a gif from asearch to be sent fully to chat
- add functionality which allows multiple pages of search
- add functionality to allow gifs to be removed from database from search (if they're just bad or wrong)
- Add better try,except code that's more robust for errors
- create small thumbnails of gifs when storing in archives
- if bot is captioning gif, automatically add to json with text inputted