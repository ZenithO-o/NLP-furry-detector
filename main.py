"""
Source Code of Furry Detector :O

Written by: @ZenithO_o on twitter (https://twitter.com/zenithO_o)
"""
# ML imports
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import model_from_json

# Twitter imports
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
import tweepy

# GUI/Other imports
from tkinter import Tk, Canvas, Label, Entry, Button, Scale
from tkinter import N, NE, S, CENTER, HORIZONTAL, NORMAL, GROOVE, FLAT, DISABLED
from PIL import Image, ImageTk
import requests
from io import BytesIO
import json
import re

"""
MAIN CLASSES
"""


class TwitterAuthenticator:
    """
    Does all the yucky
    """

    def authenticateTwitterApp(self):
        self.twitter_api_error_message = ""
        twitterkey = {}
        with open("twitter_key.json") as json_file:
            twitterkey = json.load(json_file)

        if (
            (len(twitterkey["consumer_key"]) < 20)
            or (len(twitterkey["consumer_secret"]) < 30)
            or (len(twitterkey["access_token"]) < 30)
            or (len(twitterkey["access_token_secret"]) < 30)
        ):
            self.has_key = False
            self.twitter_api_error_message = '\nAn incorrect key has been detected. Please put the correct keys in the file "Twitterkey.json"'
            return None

        self.has_key = True
        auth = OAuthHandler(twitterkey["consumer_key"], twitterkey["consumer_secret"])
        auth.set_access_token(
            twitterkey["access_token"], twitterkey["access_token_secret"]
        )
        return auth


class TwitterClient:
    """
    API handler
    """

    def __init__(self, twitter_user=None):
        self.authenticator = TwitterAuthenticator()
        self.twitter_client = API(
            self.authenticator.authenticateTwitterApp(), wait_on_rate_limit=True
        )
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user(self, user=None):
        return self.twitter_client.get_user(user)


class TextParser:
    """
    Class for cleaning up text
    """

    def cleanRawText(self, rawText):

        # remove formatting (\n)
        rawText = rawText.rstrip()

        # remove punctuation
        punctuation = [".", "!", "?", ",", "-", "#", "|", "@"]
        for i in punctuation:
            rawText = rawText.replace(i, "")

        # remove excess whitespace
        rawText = re.sub(" +", " ", rawText)

        # fix punctuation
        return rawText

    def remove_u(self, word):
        word_u = (word.encode("unicode-escape")).decode("utf-8", "strict")
        if r"\u" in word_u:
            return None
        return word

    def deEmojify(self, inputString):
        return inputString.encode("ascii", "ignore").decode("ascii")

    def wordNumCount(self, words):
        wordDict = {}
        for word in words:
            if word != None:
                try:
                    wordDict[word] += 1
                except:
                    wordDict[word] = 1
        return wordDict

    def combineDict(self, dict1, dict2):
        for key in dict2:
            if key in dict1:
                dict1[key] += dict2[key]
            else:
                dict1[key] = dict2[key]
        return dict1

    def deleteGarbage(self, wordDict):
        with open("data/stop_words.json") as json_file:
            garbage = json.load(json_file)

        for key in garbage:
            for word in garbage[key]:
                if word in wordDict:
                    del wordDict[word]
                if word.upper() in wordDict:
                    del wordDict[word.upper()]
                if word.capitalize() in wordDict:
                    del wordDict[word.capitalize()]

        for key in list(wordDict):
            try:
                if "https" in key:
                    del wordDict[key]
                if wordDict[key] == 1:
                    del wordDict[key]
                if r"\u" in key:
                    del wordDict[key]

                try:
                    int(key)
                    del wordDict[key]
                except ValueError:
                    pass

            except KeyError:
                pass

        return wordDict


class DatasetGenerator:
    """
    Class that does all the text processing for the ML model
    """

    def generateDataset(self, tweets):

        rawText = ""
        for text in [tweet.full_text for tweet in tweets]:
            rawText += " " + text
        rawText = TextParser().cleanRawText(rawText)

        userDict = self.processText(rawText)

        with open("data/word_list.json", "r") as jsonfile:
            wordDict = json.load(jsonfile)

        MostUsedWordVal = 0
        for word in userDict:
            if userDict[word] > MostUsedWordVal:
                MostUsedWordVal = userDict[word]

        inputArr = []

        for word in wordDict["set"]:
            if word in userDict:
                if userDict[word] == MostUsedWordVal:
                    inputArr.append(1)
                else:
                    inputArr.append(userDict[word] / MostUsedWordVal)
            else:
                inputArr.append(0)
        return inputArr

    def processText(self, rawText):
        rawText = rawText.casefold()
        rawText = TextParser().deEmojify(rawText)
        words = rawText.split()
        words = [TextParser().remove_u(eachWord) for eachWord in words]

        wordDict = TextParser().wordNumCount(words)
        wordDict = TextParser().deleteGarbage(wordDict)
        return wordDict


class FurryDetector:
    """
    TensorFlow ML model class
    """

    def __init__(self):
        self.model = self.loadModel()

    def loadModel(self):
        # open json file
        json_file = open("model/model.json", "r")
        loaded_model_json = json_file.read()
        json_file.close()

        # convert to keras model
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        loaded_model.load_weights("model/model.h5")

        return loaded_model

    def runModel(self, tweets):
        userDataset = [DatasetGenerator().generateDataset(tweets)]
        userDataset = np.array(userDataset)

        print(f"Created Dataset for {user.name}!\nRunning AI now...")
        prediction = self.model.predict(userDataset)[0][0]
        print(f"Prediction for {user.name}: {round((prediction*100),2)}%")

        if prediction >= 0.5:
            print(f"{user.name} is most likely a furry!")
        else:
            print(f"{user.name} is most likely NOT a furry!")

        return prediction


"""
Helper Functions
"""


def app_setup():
    detector = FurryDetector()
    client = TwitterClient()
    return detector, client


"""
Variables
"""

# Tkinter view constants
TITLE = "Furry Detector"
TITLEFONT = ("Tahoma", 18)
HEADERFONT = ("Tahoma", 10)
DEFAULTFONT = ("Tahoma", 8)
DISCLAIMERFONT = ("Tahoma", 7)
BIGFONT = ("Tahoma", 60)
BG = "gray85"
TITLE_BG = "gray80"
BUTTON_BG = "dodger blue"
BUTTON_DISABLED_BG = "gray90"
FIELD_BG = "snow"
COLOR_GRADIENT = [
    "#f00",
    "#fc0a00",
    "#fa1400",
    "#f71e00",
    "#f52800",
    "#f23100",
    "#ef3b00",
    "#ed4400",
    "#ea4c00",
    "#e85500",
    "#e55e00",
    "#e26600",
    "#e06e00",
    "#dd7500",
    "#db7d00",
    "#d88400",
    "#d68b00",
    "#d39200",
    "#d09900",
    "#cea000",
    "#cba600",
    "#c9ac00",
    "#c6b200",
    "#c3b700",
    "#c1bd00",
    "#babe00",
    "#b0bc00",
    "#a6b900",
    "#9cb600",
    "#93b400",
    "#89b100",
    "#80af00",
    "#77ac00",
    "#6fa900",
    "#66a700",
    "#5ea400",
    "#56a200",
    "#4e9f00",
    "#469d00",
    "#3f9a00",
    "#389700",
    "#319500",
    "#2a9200",
    "#239000",
    "#1d8d00",
    "#178a00",
    "#180",
    "#0b8500",
    "#058300",
    "#008000",
]

# Data variables
user = None
user_statuses = None
user_data = None
user_image = None

client = None
tweet_limit = 3200
tick_interval = 400
tweet_amt = 3200
detector = None

keras_model_error_message = ""
twitter_api_error_message = ""
has_key = False

detector, client = app_setup()
has_key = client.authenticator.has_key
twitter_api_error_message = client.authenticator.twitter_api_error_message


"""
Tkinter functions
"""


def testUser():
    input_user = twitter_entry.get()

    if input_user != "Input Twitter user here... ex: @zenithO_o":
        global user
        global user_image
        global user_statuses
        global tweet_limit

        try:
            # Get User Object
            user = client.get_user(input_user)

            # Get number of statuses
            user_statuses = user.statuses_count
            if user_statuses > tweet_limit:
                tweet_limit = 3200
            else:
                tweet_limit = user_statuses
            updateScale(tweet_limit)

            # Get Image
            img_url = user.profile_image_url_https.replace("_normal", "")

            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((128, 128))
            user_image = ImageTk.PhotoImage(img)
            twitter_user_canvas.itemconfigure(user_img, image=user_image)

            twitter_status_label.configure(
                text="Success! Found Twitter user", fg="green"
            )

            run_detector_button.configure(state=NORMAL, bg=BUTTON_BG)

        except tweepy.error.TweepError as e:
            print(e)
            user_image = ImageTk.PhotoImage(Image.open("assets/no_user.png"))
            twitter_user_canvas.itemconfigure(user_img, image=user_image)

            twitter_status_label.configure(text="Error, User not found.", fg="red")

        except:
            twitter_status_label.configure(
                text="An unknown error occured, please try again.", fg="red"
            )

    else:
        twitter_status_label.configure(text="Please enter a Twitter user", fg="red")


def runDetector():
    tweets = []
    print(f"Colletcting {tweet_amt} tweets")

    tweets.extend(
        Cursor(
            client.twitter_client.user_timeline,
            id=user.id,
            tweet_mode="extended",
            wait_on_rate_limit=True,
        ).items(tweet_amt)
    )

    print("Collected Twitter Data")

    pred = detector.runModel(tweets)

    updatePred(pred)


def updatePred(prediction):
    color = ""
    division_size = 1 / len(COLOR_GRADIENT)

    for i in range(len(COLOR_GRADIENT)):
        if prediction > i * division_size:
            color = COLOR_GRADIENT[i]

    if prediction >= 0.95:
        description_label.configure(text="You found a furry OWO")
    elif prediction >= 0.75:
        description_label.configure(text="You most likely found a furry")
    elif prediction >= 0.50:
        description_label.configure(text="You probably found a furry")
    elif prediction >= 0.25:
        description_label.configure(text="You probably didn't find a furry")
    elif prediction >= 0.05:
        description_label.configure(text="You most likely didn't find a furry")
    else:
        description_label.configure(text="You didn't find a furry")

    percentage_label.configure(text=f"{round(prediction*100,1)}%", fg=color)
    description_label.configure(fg=color)


def updateScale(tweet_limit):
    global tick_interval

    tick_interval = tweet_limit // 8

    tweet_scale.configure(state=NORMAL, to=tweet_limit, tickinterval=tick_interval)
    pass


def updateAmt(self):
    global tweet_amt
    tweet_amt = int(tweet_scale.get())


"""
MAIN TKINTER
"""

# INITIAL SETUP
root = Tk()
root.minsize(400, 500)
root.maxsize(600, 800)
root.title(TITLE)
root.grid_columnconfigure(1, weight=1)
root.wm_iconbitmap("assets/paw_icon.ico")
root.configure(bg=BG)

# APP TITLE LABEL
title_label = Label(root, text=TITLE, bg=TITLE_BG, anchor=CENTER, font=TITLEFONT)

title_label.grid(
    row=0,
    column=1,
    sticky="nsew",
)

# CREDIT HEADER LABEL
header_label = Label(
    root, text="Developed by @ZenithO_o on Twitter", bg=BG, anchor=N, font=HEADERFONT
)

header_label.grid(row=1, column=1, sticky="nsew")

# IMAGE CANVAS
twitter_user_canvas = Canvas(root, width=128, height=128, bg=BG)
twitter_user_canvas.grid(row=3, column=1)

# USER IMAGE INITIALIZATION
user_image = ImageTk.PhotoImage(Image.open("assets/no_user.png"))
user_img = twitter_user_canvas.create_image(129, 0, anchor=NE, image=user_image)

# TWITTER ACCOUNT ENTRY FIELD
twitter_entry = Entry(
    root, width=40, bg=FIELD_BG, fg="gray30", bd=0, justify=CENTER, font=DEFAULTFONT
)

twitter_entry.grid(row=4, column=1, pady=10)

twitter_entry.insert(0, "Input Twitter user here... ex: @zenithO_o")

# TWITTER ACCOUNT CHECK BUTTON
twitter_button = Button(
    root,
    text="Get User",
    padx=10,
    pady=5,
    bd=0,
    bg=BUTTON_BG,
    fg="snow",
    font=DEFAULTFONT,
    justify=CENTER,
    command=testUser,
)

twitter_button.grid(row=5, column=1)

# TWITTER BUTTON STATUS LABEL
twitter_status_label = Label(
    root, text="", bg=BG, fg="red", anchor=N, justify=CENTER, font=DISCLAIMERFONT
)

twitter_status_label.grid(row=6, column=1)

# TWEET NUM SCALE
tweet_scale = Scale(
    root,
    font=DEFAULTFONT,
    label="Number of tweets to scrape:",
    from_=0,
    to=tweet_limit,
    relief=FLAT,
    bg=BG,
    bd=0,
    orient=HORIZONTAL,
    sliderlength=20,
    sliderrelief=GROOVE,
    highlightthickness=0,
    length=300,
    fg="gray20",
    troughcolor=FIELD_BG,
    tickinterval=tick_interval,
    state=DISABLED,
    command=updateAmt,
)

tweet_scale.grid(row=7, column=1)

# RUN DETECTOR BUTTON
run_detector_button = Button(
    root,
    text="Run detector",
    bg=BUTTON_DISABLED_BG,
    fg="snow",
    font=DEFAULTFONT,
    justify=CENTER,
    padx=10,
    pady=5,
    bd=0,
    state=DISABLED,
    command=runDetector,
)

run_detector_button.grid(row=8, column=1)

# RUN DETECTOR BUTTON STATUS LABEL
run_detector_status_label = Label(
    root, text="", bg=BG, anchor=N, justify=CENTER, font=DISCLAIMERFONT
)

run_detector_status_label.grid(row=9, column=1)

# RESULT PERCENTAGE
percentage_label = Label(
    root, text="0.0%", bg=BG, anchor=CENTER, fg="gray60", font=BIGFONT
)
percentage_label.grid(row=10, column=1)

# RESULT DESCRIPTION
description_label = Label(
    root,
    text="Input a user to get started",
    bg=BG,
    anchor=CENTER,
    fg="gray60",
    font=HEADERFONT,
)
description_label.grid(row=11, column=1)

# ERROR MESSAGES
error_label = Label(
    root,
    text=keras_model_error_message + twitter_api_error_message,
    bg=BG,
    fg="red",
    anchor=S,
    pady=30,
    justify=CENTER,
    font=DISCLAIMERFONT,
)

error_label.grid(row=100, column=1)


root.mainloop()
