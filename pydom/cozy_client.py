
from urllib.parse import quote_plus

import requests

from pydom import config


class CozyTouchClient:

    def __init__(self):
        self.session = requests.session()
        self.token = None
        self.jwt = None

        self.login()

    @staticmethod
    def get_token(username, password):

        r = requests.post('https://apis.groupe-atlantic.com/token', params={
            "grant_type": "password",
            "username": username,
            "password": password
        }, headers={
            "Authorization": "Basic Q3RfMUpWeVRtSUxYOEllZkE3YVVOQmpGblpVYToyRWNORHpfZHkzNDJVSnFvMlo3cFNKTnZVdjBh"
        })

        return r.json()['access_token']

    def get_jwt(self):

        if self.token is None: 
            self.token = self.get_token(config.get('COZYTOUCH_USERNAME'), config.get('COZYTOUCH_PASSWORD'))

        r = requests.get('https://apis.groupe-atlantic.com/magellan/accounts/jwt', headers={
            "Authorization": f'Bearer {self.token}'
        })

        if 'Invalid Credentials' in r.text:
            self.token = None
            return self.get_jwt()

        return r.json().strip()

    def login(self):

        self.jwt = self.get_jwt()

        _ = self.session.post("https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/login", data={
            'jwt': self.jwt
        })

    def get_state(self, deviceURL, nameState):

        _deviceURL = quote_plus(deviceURL)

        r = self.session.get(f"https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/setup/devices/{_deviceURL}/states/{nameState}")

        return r.json()
    
    def check_session(self):

        r = self.session.get("https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/setup/devices")
        if r.status_code != 200:
            self.login()
        
        r = self.session.get("https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/setup/devices")
        if r.status_code != 200:
            raise Exception("")

        return self
