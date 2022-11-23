# NLP-furry-detector
This is the Furry Detector program as seen on my [YouTube](https://youtube.com/c/FurryMemes)!

It uses the Twitter API, TensorFlow, and Tkinter to make an all-in-one furry detecting program.

## How it Works
This machine learning model uses the text given from tweets to determine if a Twitter user is furry or not (it can also be applied more generally to non-twitter applications, but results may vary).

First it takes a Twitter user, and collects their tweets. Then, using `word_list.json`, a 1000 length word vector is generated that has the counts of all the words used. It is normalized between [0-1], 1 being the most common occuring work, and 0 being not used at all. Finally, this word vector is passed through the model, and a confidence score is given.

## Usage
For my own sanity, the classes in this repository are **NOT** packageble and are self contained. `main.py` takes advantage of this, and is a simply GUI interface for you to take advantage of and sample the project. Here are some of the different files you can find:

### Model
This directory contains the `furry_detector.py` and `parser.py` files. Here, you can parse text and run it through the `FurryDetector` class to determine if the text written was done so by a furry.

### Twitter
This directory contains the `wrapper.py` file. This has a basic class that does API calls to Twitter for tweets of a user, and the user itself. It is barebones, and is really only meant for usage within `main.py`.

### Main.py
In the file `twitter_key.json` you must put your bearer token and whether or not you want to use Twitter v1.1. By default, this program will use v2.0

Read Twitter's tutorial [here](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api) for obtaining an API key.

Run `main.py` to see a GUI for selecting a Twitter User! Type who you want, and the model will run on their account to see if they are a furry! :D

## Other

**Please be sure to read `requirements.txt` for the modules used**

#### Contributions
Contributions are welcome!

I am always willing to look at PR's and issues if you think there is something that can be fixed or added :)

-----
#### *2022-11-22 Update*
This repository has gotten a long overdue makeover. I have refactored the project so that the code is much cleaner (and does not look like it was written by someone who only had 6 months experience with Python), and also so that it runs somewhat faster.

## License

[MIT](https://choosealicense.com/licenses/mit/)
