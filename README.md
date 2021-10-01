# Giffy-Bot
A mutlipurpose repos designed to allow the de-captioning and tagging of gifs, as well as other functionality to do with the catagorsing and organising of gifs.

The repos also provides abstraction of these commands through the discord bot Giffy-Bot


Current list of Bot Commands
- decaption a caption gif
- return text in a gif
- store last gif posted to server

Aims of the bot
- the user is able to enter a sentence to be used in a caption gif and the program can return an appropriate captionless gif to use
    - This could be achieved by analysing each word in the sentence, seperating it into nouns, adjectives, verbs. Then using those as search queries
    - Somehow scraping a large list of caption gifs, analysing the words they contain, grouping them together under similar subjects, and then using either a Neural Network or some   math to find the correct gif (certain words could link to gifs with a higher average red colour etc.) 

USE NLTK FOR WORD PROCESSING
CHECK THAT PIXEL 0,0 OF FIRST AND SECOND FRAME REMAINS CONSTANT