import requests as r
from queue import Queue
from threading import enumerate
from time import time
import json

class Static_methods:
    @staticmethod
    def prepare_proxy_to_insert_into_database(data):
        prepared_data = []
        for each in data:
            value = (each['ip'],each['port'],each['protocol'],each['server_response_time'],each['check_time'])
            prepared_data.append(value)

        return prepared_data
    @staticmethod
    def prepare_market_prices_to_insert_into_database(data):
        result = []
        for name,value in data.items():
            result.append((name,value["best_offer"]))
        return result
    @staticmethod
    def prepare_dmarket_prices_to_insert_into_database(data):
        result = []
        for name,value in data.items():
            result.append((name,value["best_offer"],value["best_order"]))
        return result
    @staticmethod
    def prepare_cookies(cookies,old_cookie = None):
        if old_cookie != None:
            ret_cookies = old_cookie
        else:
            ret_cookies = {}
        for each in cookies:
            ret_cookies[each.name] = each.value
        return ret_cookies

    @staticmethod
    def prepare_buff_163_cookies(cookies):
        prepared_cookies = {}
        for each in cookies:
            name = each.get('name')
            value = each.get('value')
            if name != None and value != None:
                prepared_cookies[name] = value
        return prepared_cookies
    @staticmethod
    def validate_steam_authorization(main_func):
        def wrapper(self,username=None):
            url = "https://steamcommunity.com/actions/GetNotificationCounts"
            headers = {
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
                'Referer': 'https://steamcommunity.com/market/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            try:
                if username == None:
                    username = list(self.cookies_dict.keys())[0]
                cookies = {
                    "steamLoginSecure":self.cookies_dict[username]["steamLoginSecure"]
                }
                resp = r.get(url,headers=headers,cookies=cookies,allow_redirects=False,timeout=15)
                if resp.status_code == 200:
                        self.return_data.put({"username":username,"relogin":False,"status":True})
                        return main_func(self,username)
                elif resp.status_code == 401:
                    print(f"Steam Unauthorized user: {username}")
                    self.return_data.put({"username":username,"relogin":True,"status":False})
                    return {"username":username,"relogin":True,"status":False}
                else:
                    print(f"Status code error during validation of Steam cookie: {resp.status_code}")
                    self.return_data.put({"username":username,"relogin":False,"status":None})
                    return {"username":username,"relogin":False,"status":None}
            except Exception as e:
                print(f"Error during validation of Steam cookie: {e}")
                self.return_data.put({"username":username,"relogin":False,"status":None})
                return {"username":username,"relogin":False,"status":None}
        return wrapper

    @staticmethod
    def validate_buff_163_authorization(main_func):
        def wrapper(self,phone_number=None):
            if phone_number == None:
                phone_number = list(self.cookies_dict.keys())[0]
            cookies = {"session":self.cookies_dict[phone_number]["session"]}
            params = {
                "game": self.game,
                "page_num": 3,
                "page_size": 20,
                "_": int(time()*1000)
            }
            try:
                resp = r.get(self.url,headers=self.headers,params=params,cookies=cookies,allow_redirects=False,timeout=15)

                if resp.status_code == 200:
                        json_data = json.loads(resp.text)
                        if json_data["code"] == "OK":
                            self.return_data.put({"phone_number":phone_number,"relogin":False,"status":True})
                            return main_func(self,phone_number)
                        else:
                            print(f"Buff Unauthorized user: {phone_number}")
                            self.return_data.put({"phone_number":phone_number,"relogin":True,"status":False})
                            return {"phone_number":phone_number,"relogin":True,"status":False}
                else:
                    print(f"Status code error during validation of Buff cookie: {resp.status_code}")
                    self.return_data.put({"phone_number":phone_number,"relogin":False,"status":None})
                    return {"phone_number":username,"relogin":False,"status":None}
            except Exception as e:
                print(f"Error during validation of Buff cookie: {e}")
                self.return_data.put({"phone_number":phone_number,"relogin":False,"status":None})
                return {"phone_number":phone_number,"relogin":False,"status":None}
            #return main_func(self,username)
        return wrapper

    @staticmethod
    def create_proxy_pool(data):
        proxy_pool = Queue()
        for each in data:
            info = {
                "ip":each[0],
                "proxies": {
                            "http":f"{each[2]}://{each[0]}:{each[1]}",
                            "https":f"{each[2]}://{each[0]}:{each[1]}",
                            }
                    }
            proxy_pool.put(info)
        return proxy_pool

    @staticmethod
    def thread_exists(name):
        for each in enumerate():
            if each.name == name:
                return True
        return False
