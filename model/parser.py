from pathlib import Path
from collections import Counter
import json
import re

PARSE_PATH = Path(__file__).parent / 'parse_data'

def _load_word_list() -> dict:
    """Helper function to get word list json

    Returns:
        dict: 0 populated dictionary of word list
    """
    with open(PARSE_PATH / 'word_list.json') as json_file:
        data = json.load(json_file)

    return {k:0 for k in data['set']}

def parse_tweets(tweets: list[str]) -> list[float]:
    """Helper function to convert a list of tweets into something usable by
    `parse_text`. Returns what `parse_text` would return.

    Args:
        tweets (list[str]): The list of tweets to convert

    Returns:
        list[float]: output word vector
    """
    text = ' '.join(map(str, tweets))
    return parse_text(text)


def parse_text(text: str) -> list[float]:
    """Convert text into a word vector usable by `FurryDetector`.

    Args:
        text (str): input text to convert

    Returns:
        list[float]: output word vector
    """
    word_list = _load_word_list()

    lines = text.lower().splitlines(keepends=False)
    words = []
    for line in lines:
        words.extend(line.split(' '))

    # O(1000*n)
    # misses many values, but the overall trend should cut through noise. Other
    # parsing tricks, like checking if re.sub(r'\W', '', word) would take too
    # long, so this will suffice.
    highest = 1
    for key in word_list:
        for word in words:
            if key == word:
                word_list[key] += 1
        highest = max(word_list[key], highest)

    return [word_list[word]/highest for word in word_list]