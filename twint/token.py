import re
import time

import requests
import logging as logme


class TokenExpiryException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

        
class RefreshTokenException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        

class Token:
    def __init__(self, config):
        self._session = requests.Session()
        self.config = config
        self._retries = 5
        self._timeout = 10
        self.url = 'https://twitter.com'

    def get_tokens(self):
        s = self._session
        s.headers.update({
            "user-agent"	:	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
            "accept"	:	"*/*",
            "accept-language"	:	"de,en-US;q=0.7,en;q=0.3",
            "accept-encoding"	:	"gzip, deflate, br",
            "te"	:	"trailers",
        })
        try:
            # get guest_id cookie
            r = s.get("https://twitter.com")
    
            # get auth token
            main_js = s.get(
                "https://abs.twimg.com/responsive-web/client-web/main.e46e1035.js",
            ).text
            token = re.search(r"s=\"([\w\%]{104})\"", main_js)[1]
            s.headers.update({"authorization"	:	f"Bearer {token}"})
    
            # activate token and get guest token
            guest_token = s.post(
                "https://api.twitter.com/1.1/guest/activate.json").json()["guest_token"]
            s.headers.update({"x-guest-token"	:	guest_token})
            return guest_token
        except:
            return None

    def refresh(self):
        logme.debug('Retrieving guest token')
        res = self.get_tokens()
        if res:
            logme.debug('Found guest token in HTML')
            self.config.Guest_token = res
        else:
            self.config.Guest_token = None
            raise RefreshTokenException('Could not find the Guest token in HTML')
