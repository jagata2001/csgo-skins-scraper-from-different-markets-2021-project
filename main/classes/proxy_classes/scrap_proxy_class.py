import requests as r
from queue import Queue
import json
from sys import exit


class Scrap_proxy:
    def __init__(self,url,limit=50):
        self.url = url
        self.proxy_data = []
        self.params  = {
            'limit': limit,
            'page': '1',
            'sort_by': 'lastChecked',
            'sort_type': 'desc',
            'protocols': 'https,socks4,socks5',
            'anonymityLevel': ['elite', 'anonymous']
        }

    def get_all_proxy_data_from_returned_json(self,max_try=None,proxy_limit=5000):
        page = 1
        try_count = 0
        exit_from_main_loop = False
        while True:
            self.params['page'] = page
            try:
                resp = r.get(self.url,self.params,timeout=15)
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    for each in data["data"]:
                        self.proxy_data.append(each)
                        if len(self.proxy_data)>=proxy_limit:
                            exit_from_main_loop = True
                            break
                    if len(data["data"]) == 0 or exit_from_main_loop:
                        break
                    page+=1

                else:
                    try_count+=1
                    print(f"Scrap proxy status code error: {resp.status_code}")
            except KeyboardInterrupt:
                exit("Exit by Keyboard")
            except Exception as e:
                try_count+=1
                print(f"Scrap proxy error: {e}")
            if max_try != None and max_try<=try_count:
                exit("Scrap proxy max try count exceeded")
