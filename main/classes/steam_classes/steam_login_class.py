from classes.static_methods_class import Static_methods

import requests as r
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from time import time
import json


class Steam_login:
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.cookies = {}
        self.encrypted_password=""
        self.timestamp = 0

    def get_first_cookies(self):
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://steamcommunity.com/market/',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        params = {
            'goto':'market/'
        }
        try:
            resp = r.get('https://steamcommunity.com/login/home/', headers=headers, params=params)
            if resp.status_code == 200:
                cookies = Static_methods.prepare_cookies(resp.cookies)
                if len(cookies) == 0:
                    print("Cookies dict is empty!")
                    return False
                else:
                    self.cookies = cookies
                    return True
            else:
                print(f"Status code error during first load: {resp.status_code}")
                return False
        except Exception as e:
            print(f"Something went wrong during first load error: {e}")
            return False


    def encrypt_password(self,publickey_mod,publickey_exp,password):
        mod = int(publickey_mod, 16)
        exp = int(publickey_exp, 16)
        rsa_key = RSA.construct((mod,exp))
        rsa = PKCS1_v1_5.PKCS115_Cipher(rsa_key)
        encr_password = base64.b64encode(rsa.encrypt(password.encode()))
        return encr_password.decode()

    def get_rsa_key(self):
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://steamcommunity.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://steamcommunity.com/login/home/?goto=',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        data = {
                "username":self.username,
                "donotcache": int(time()*100)
                }
        try:
            resp = r.post("https://steamcommunity.com/login/getrsakey/",cookies=self.cookies,data=data,headers=headers)
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                if json_data["success"] == True:
                    self.encrypted_password = self.encrypt_password(
                            json_data["publickey_mod"],
                            json_data["publickey_exp"],
                            self.password
                                        )
                    self.timestamp = json_data["timestamp"]
                    return True
                else:
                    print("Returned not excpected data during getting rsa key")
                    print(json_data)
                    return False

            else:
                print(f"Status code error during getting rsa key: {resp.status_code}")
                return False
        except json.decoder.JSONDecodeError:
            print("Incorrect returned response text json can't load it")
            return False
        except KeyError:
            print("Returned json data doesn't contain specific key")
            return False
        except:
            print(f"Something went wrong during getting rsa key")
            return False

    def do_login(self):
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://steamcommunity.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://steamcommunity.com/login/home/?goto=',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        data = {
            "donotcache": int(time()*100),
            "password":self.encrypted_password,
            "username": self.username,
            "twofactorcode":"",
            "emailauth":"",
            "loginfriendlyname":"",
            "captchagid": "-1",
            "captcha_text":"",
            "emailsteamid":"",
            "rsatimestamp": self.timestamp,
            "remember_login": "false",
            "tokentype": "-1"
        }
        try:
            print("The entry process is underway...")
            resp = r.post("https://steamcommunity.com/login/dologin/",cookies=self.cookies,data=data,headers=headers)
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                if json_data["success"] == True:
                    cookies = Static_methods.prepare_cookies(resp.cookies,self.cookies)
                    self.cookies = cookies
                    return True
                else:
                    print(f"username: {self.username}, {json_data['message']}")
                    return 0

            else:
                print(f"Status code error during login: {resp.status_code}")
                return False
        except json.decoder.JSONDecodeError:
            print("Incorrect returned response text during login json can't load it")
            return False
        except KeyError:
            print("Returned json data doesn't contain specific key")
            return False
        except:
            print(f"Something went wrong during making login")
            return False






#
