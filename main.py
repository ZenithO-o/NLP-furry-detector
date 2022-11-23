import requests
from io import BytesIO
import json

from twitter.wrapper import BasicTwitterWrapper
from model.furry_detector import FurryDetector
from model.parser import parse_tweets

from tkinter import Tk, Canvas, Label, Entry, Button, Scale
from tkinter import N, NE, S, CENTER, HORIZONTAL, NORMAL, GROOVE, FLAT, DISABLED
from PIL import Image, ImageTk

def load_twitter_api() -> BasicTwitterWrapper:
    with open('twitter_key.json') as json_file:
        data = json.load(json_file)
    bearer = data['bearer_token']
    v1_1   = data['v1.1']

    return BasicTwitterWrapper(bearer_token=bearer, v1_1=v1_1)

def create_root() -> Tk:
    root = Tk()
    root.minsize(400, 500)
    root.maxsize(600, 800)
    root.title(TITLE)
    root.grid_columnconfigure(1, weight=1)
    root.wm_iconbitmap("assets/paw_icon.ico")
    root.configure(bg=BG)

    return root

if __name__ == '__main__':
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
    user_image = None

    tweet_limit = 3200
    tick_interval = 400
    tweet_amt = 3200

    api = load_twitter_api()
    detector = FurryDetector()


    """
    Tkinter functions
    """
    def test_user():
        input_user = twitter_entry.get()

        global user
        global user_image

        try:
            input_user = input_user.replace('@', '')
            user = api.get_user(input_user)

            if user:
                # Get Image
                img_url = user.profile_image_url.replace("_normal", "")

                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((128, 128))
                user_image = ImageTk.PhotoImage(img)
                twitter_user_canvas.itemconfigure(user_img, image=user_image)

                twitter_status_label.configure(
                    text="Success! Found Twitter user", fg="green"
                )

                run_detector_button.configure(state=NORMAL, bg=BUTTON_BG)
            else:
                raise ValueError('User does not exist')

        except Exception as e:
            print(e)
            user_image = ImageTk.PhotoImage(Image.open("assets/no_user.png"))
            twitter_user_canvas.itemconfigure(user_img, image=user_image)

            twitter_status_label.configure(text=f'Error, User "{input_user}" not found.', fg="red")


    def run_detector():
        tweet_amt = int(tweet_scale.get())
        tweets = api.get_tweets(user.screen_name, tweet_amt)
        in_arr = parse_tweets(tweets)

        pred = detector.run(input_arr=in_arr)

        update_pred(pred)


    def update_pred(prediction):
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
        command=test_user,
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
        command=run_detector,
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
        text='',
        bg=BG,
        fg="red",
        anchor=S,
        pady=30,
        justify=CENTER,
        font=DISCLAIMERFONT,
    )

    error_label.grid(row=100, column=1)


    root.mainloop()