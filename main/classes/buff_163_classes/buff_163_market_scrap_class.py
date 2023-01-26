import requests as r
import json
from queue import Queue,Empty
from time import time

from classes.static_methods_class import Static_methods
from classes.database_classes.database_proxy_class import Database_proxy

class Buff163_scrap:
    def __init__(self,game,cookies_dict,proxy_pool):
        self.game = game
        self.cookies_dict=cookies_dict
        self.proxy_pool = proxy_pool
        self.url = "https://buff.163.com/api/market/goods"
        self.pages = Queue()
        #this is for multithreading to catch returned data
        self.return_data = Queue()
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://buff.163.com/market/csgo',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.main_data = {}
    @Static_methods.validate_buff_163_authorization
    def get_page_quantity(self,phone_number=None):
        if phone_number == None:
            phone_number = list(self.cookies_dict.keys())[0]
        cookies = {"session":self.cookies_dict[phone_number]["session"]}
        params = {
            "game": self.game,
            "page_num": 1,
            "page_size": 80,
            "_": int(time()*1000)
        }
        try:
            resp = r.get(self.url,params=params,cookies=cookies,headers=self.headers,timeout=15)
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                if json_data["code"] == "OK":
                    for page in range(1,json_data["data"]["total_page"]+1):
                        self.pages.put(page)
                    return True
                else:
                    print(f"Invalid returned json data during Buff market page quantity scarping. {json_data}")
                    return False
            else:
                print(f"Status code error Buff market page quantity scarpin. {resp.status_code}")
                return False
        except Exception as e:
            print(f"Error during Buff market page quantity scarping. error: {e}")
            return False
    def parse_prices_from_returned_json(self,items):
        for each in items:
            self.main_data[each["name"]] = {"steam_price":float(each["sell_min_price"])}

    @Static_methods.validate_buff_163_authorization
    def buff_163_market_price_scrap(self,phone_number=None):
        if phone_number == None:
            phone_number = list(self.cookies_dict.keys())[0]
        cookies = {"session":self.cookies_dict[phone_number]["session"]}
        params = {
            "game": self.game,
            "page_num": 1,
            "page_size": 80,
            "_": int(time()*1000)
        }
        requests_exceptions = (r.exceptions.BaseHTTPError,r.exceptions.ChunkedEncodingError,r.exceptions.ConnectTimeout,r.exceptions.ConnectionError,r.exceptions.ContentDecodingError,r.exceptions.FileModeWarning,r.exceptions.HTTPError,r.exceptions.InvalidHeader,r.exceptions.InvalidProxyURL,r.exceptions.InvalidSchema,r.exceptions.InvalidURL,r.exceptions.MissingSchema,r.exceptions.ProxyError,r.exceptions.ReadTimeout,r.exceptions.RequestException,r.exceptions.RequestsDependencyWarning,r.exceptions.RequestsWarning,r.exceptions.RetryError,r.exceptions.SSLError,r.exceptions.StreamConsumedError,r.exceptions.Timeout,r.exceptions.TooManyRedirects,r.exceptions.URLRequired,r.exceptions.UnrewindableBodyError)
        get_proxy = True
        proxies = None
        db = Database_proxy("jagata","678946icom","steam_skin_data")
        while True:
            try:
                if get_proxy == True:
                    proxies = self.proxy_pool.get(False)
                    get_proxy=False
                page = self.pages.get(False)
                params["page_num"] = page
                resp = r.get(self.url,headers=self.headers,params=params,cookies=cookies,proxies=proxies["proxies"],timeout=10)
                if resp.status_code == 200:
                    json_data = json.loads(resp.text)
                    if json_data["code"] == "OK":
                        self.parse_prices_from_returned_json(json_data["data"]["items"])
                    else:
                        print(f"Buff returned incorrect code in json_data: {json_data}")
                elif resp.status_code == 429:
                    db.update_proxy_after_use(proxies["ip"])
                    proxies = self.proxy_pool.get(False)
                    self.pages.put(page)

            except requests_exceptions:
                db.update_proxy_after_use(proxies["ip"])
                proxies = self.proxy_pool.get(False)
                self.pages.put(page)

            except Empty:
                if self.proxy_pool.qsize() == 0:
                    print(f"Empty proxy pool so program have to break")
                if proxies != None:
                    db.update_proxy_after_use(proxies["ip"])
                db.close()
                print("end working")
                break
            except Exception as e:
                print(f"Error during scraping Buff skin prices: {e}")


#
