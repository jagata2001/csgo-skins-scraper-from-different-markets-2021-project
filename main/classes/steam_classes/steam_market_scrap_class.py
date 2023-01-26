from classes.static_methods_class import Static_methods
from classes.database_classes.database_proxy_class import Database_proxy

import requests as r
import json
from queue import Queue,Empty


class Steam_market_scrap:
    def __init__(self,appid,cookies_dict,proxy_pool):
        self.appid=appid
        self.cookies_dict=cookies_dict
        self.proxy_pool = proxy_pool
        self.url = "https://steamcommunity.com/market/search/render/"
        self.start_from = Queue()
        #this is for multithreading to catch returned data
        self.return_data = Queue()
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://steamcommunity.com/market/search?appid={appid}',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.main_data = {}
        self.main_data_queue = Queue()

        #######################################################################

        self.deletethis = []

    @Static_methods.validate_steam_authorization
    def get_skin_quantity(self,username=None):
        if username == None:
            cookies = {
                "steamLoginSecure":list(self.cookies_dict.values())[0]["steamLoginSecure"]
            }
        else:
            cookies = {
                "steamLoginSecure":self.cookies_dict[username]["steamLoginSecure"]
            }
        params = {
            'query': '',
            'start': '0',
            'count': '10',
            'search_descriptions': '0',
            'sort_column': 'popular',
            'sort_dir': 'desc',
            'appid': self.appid,
            'norender':1
        }

        try:
            resp = r.get(self.url,params=params,cookies=cookies,headers=self.headers,timeout=15)
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                if json_data["success"] == True:
                    quantity = json_data["total_count"]
                    print(f"steam skin quantity that have to be scraped: {quantity}")
                    for each in range(0,quantity,100):
                        self.start_from.put(each)
                    return True
                else:
                    print(f"Returned json is not valid")
                    return False
            else:
                print(f"Status code error during getting skin quantity: {resp.status_code}")
                return False
        except Exception as e:
            print(f"Steam Error: {e}")
            return False

    def parse_returned_json_for_prices(self,results):
        chunk = {}
        for each in results:
            self.main_data[each["name"]] = {"best_offer":float(each["sell_price_text"].replace(",","").replace("$",""))}
            chunk[each["name"]] = {"best_offer":float(each["sell_price_text"].replace(",","").replace("$",""))}
        self.main_data_queue.put(chunk)


    @Static_methods.validate_steam_authorization
    def steam_price_scrap(self,username=None):
        if username == None:
            cookies = {
                "steamLoginSecure":list(self.cookies_dict.values())[0]["steamLoginSecure"]
            }
        else:
            cookies = {
                "steamLoginSecure":self.cookies_dict[username]["steamLoginSecure"]
            }
        params = {
            'query': '',
            'start': '0',
            'count': '100',
            'search_descriptions': '0',
            'sort_column': 'popular',
            'sort_dir': 'desc',
            'appid': self.appid,
            'norender':1
        }
        requests_exceptions = (r.exceptions.BaseHTTPError,r.exceptions.ChunkedEncodingError,r.exceptions.ConnectTimeout,r.exceptions.ConnectionError,r.exceptions.ContentDecodingError,r.exceptions.FileModeWarning,r.exceptions.HTTPError,r.exceptions.InvalidHeader,r.exceptions.InvalidProxyURL,r.exceptions.InvalidSchema,r.exceptions.InvalidURL,r.exceptions.MissingSchema,r.exceptions.ProxyError,r.exceptions.ReadTimeout,r.exceptions.RequestException,r.exceptions.RequestsDependencyWarning,r.exceptions.RequestsWarning,r.exceptions.RetryError,r.exceptions.SSLError,r.exceptions.StreamConsumedError,r.exceptions.Timeout,r.exceptions.TooManyRedirects,r.exceptions.URLRequired,r.exceptions.UnrewindableBodyError)
        get_proxy = True
        proxies = None
        db = Database_proxy("jagata","678946icom","steam_skin_data")
        while True:
            try:
                try:
                    if get_proxy == True:
                        proxies = self.proxy_pool.get(False)
                        get_proxy=False
                    start = self.start_from.get(False)
                    params["start"] = start
                    resp = r.get(self.url,headers=self.headers,params=params,cookies=cookies,proxies=proxies["proxies"],timeout=10)
                    if resp.status_code == 200:
                        json_data = json.loads(resp.text)
                        if json_data["success"] == True:
                            self.parse_returned_json_for_prices(json_data["results"])
                            self.deletethis.append(len(json_data["results"]))
                        else:
                            print(f"Steam_market_scrap: {json_data}")
                    elif resp.status_code == 429:
                        #print("Changing proxy cause of error 429 status code")
                        db.update_proxy_after_use(proxies["ip"])
                        proxies = self.proxy_pool.get(False)
                        self.start_from.put(start)

                except requests_exceptions:#(r.exceptions.ConnectTimeout,r.exceptions.ConnectionError,r.exceptions.HTTPError,r.exceptions.InvalidProxyURL,r.exceptions.ProxyError,r.exceptions.ReadTimeout,r.exceptions.SSLError,r.exceptions.Timeout):
                    db.update_proxy_after_use(proxies["ip"])
                    proxies = self.proxy_pool.get(False)
                    self.start_from.put(start)

                    #print("Changing proxy...")

            except Empty:
                if self.proxy_pool.qsize() == 0:
                    print(f"Empty proxy pool so program have to break")
                if proxies != None:
                    db.update_proxy_after_use(proxies["ip"])
                db.close()
                break
            except Exception as e:
                print(f"Error during scraping skin prices: {e}")










#
