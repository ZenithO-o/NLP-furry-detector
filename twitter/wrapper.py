import requests
from dataclasses import dataclass

@dataclass
class TwitterUser:
    id: int
    name: str
    screen_name: str
    profile_image_url: str

@dataclass
class Tweet:
    id: int
    text: str

    def __str__(self) -> str:
        return self.text


class TwitterWrapperError(Exception):
    """An invalid parameter was passed somewhere in `BasicTwitterWrapper`"""
    pass

class BasicTwitterWrapper:
    """This class is a specialized wrapper for the Twitter API.
    
    Note: This is NOT designed to be expanded on, it's really only for
    compatibility sake and performance. It is not very safe, and very much
    assumes you use it correctly. Burden of failure is on user, not this
    class.
    """
    def __init__(self, bearer_token : str, v1_1: bool = False) -> None:
        """`BasicTwitterWrapper` can be used as an instance to iteract with Twitter API.
        
        Get a Twitter user's basic info and tweets using their 'screen_name'

        Args:
            bearer_token (str): The Bearer Token you recieve when creating a new Twitter App
            v1_1 (bool, optional): Which version of the Twitter API to use. Deafult is v2.0
        """
        self._header = {"authorization": f"Bearer {str(bearer_token)}"}
        self._sess   = requests.Session()
        self._v1_1   = True if v1_1 else False # No sneaky `None`'s >:(
    
    def get_user(self, screen_name : str) -> TwitterUser:
        """Collect a Twitter user's basic info.

        Args:
            screen_name (str): The Twitter handle of the user.

        Raises:
            TwitterWrapperError: The API Wrapper recieves an error code.

        Returns:
            TwitterUser: Dataclass containing user info.
        """
        if self._v1_1:
            url = 'https://api.twitter.com/1.1/users/lookup.json'
            params = {'screen_name' : screen_name}
        else:
            url = f'https://api.twitter.com/2/users/by/username/{screen_name}'
            params = {'user.fields' : 'profile_image_url'}

        result = self._sess.get(url, params=params, headers=self._header)

        if result.status_code == 200:
            if self._v1_1:
                data = result.json()[0]
            else:
                data = result.json().get('data')
            
            if data:
                return TwitterUser(data.get('id'), data.get('name'), data.get('username') if data.get('username') else data.get('screen_name'), data.get('profile_image_url'))
        else:
            raise TwitterWrapperError(f'{result.status_code} was recieved from {url}')


    def get_tweets(self, screen_name : str, max_tweets : int = 3200) -> list[Tweet]:
        """Collect the tweets of a user based on their `screen_name`
        
        Collects as many tweets as possible, up to the 3200 tweet
        limit that Twitter enforces.

        Args:
            screen_name (str): The Twitter handle of the user.
            max_tweets (int, optional): Number of tweets to collect. Defaults to 3200.

        Raises:
            ValueError: The user does not exist, therefore, tweets cannot be found.
            TwitterWrapperError: The API Wrapper recieves an error code.


        Returns:
            list[Tweet]: A list of up to 3200 Tweets of the Twitter user.
        """
        max_tweets = min(3200, max_tweets)
        user = self.get_user(screen_name)
        if user:
            if self._v1_1:
                url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
                params = {
                    "screen_name" : screen_name,
                    "count"       : min(200, max_tweets),
                    "tweet_mode"  : 'extended'
                    }
            else:
                url = f'https://api.twitter.com/2/users/{user.id}/tweets'
                
                params = {
                    "max_results" : 100,
                    'tweet.fields' : 'text'
                    }
        else:
            raise ValueError(f'"{screen_name}" does not exist!')

        tweets = []
        status_code = 200
        left = max_tweets
        while status_code == 200 and left:
            result = self._sess.get(url, params=params, headers=self._header)
            status_code = result.status_code

            if status_code == 200:
                data = result.json()

                if self._v1_1:
                    data:list[dict] # If working as intended, will be this type
                    if data:
                        tweets.extend([Tweet(tweet['id_str'], tweet['full_text']) for tweet in data])
                        params['max_id'] = str(data[-1].get('id', 1) - 1)
                        left -= len(data)
                        params['count']  = min(200, left)
                    else:
                        break
                else:
                    data:dict # If working as intended, will be this type
                    meta = data['meta']
                    data = data['data']
                    
                    # add data
                    tweets.extend([Tweet(tweet['id'], tweet['text']) for tweet in data])

                    # paginate
                    meta:dict
                    if meta.get('next_token'):
                        params['pagination_token'] = meta['next_token']
                    else:
                        break
            else:
                raise TwitterWrapperError(f'{result.status_code} was recieved from {url}')

        return tweets
