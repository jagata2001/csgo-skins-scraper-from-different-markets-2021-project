import requests as r
from nacl.bindings import crypto_sign
from queue import Queue,Empty
from time import time
import json

class Dmarket_scrap:
    def __init__(self,url,api_keys,skin_names):
        self.url = url
        self.__api_keys = api_keys
        self.skin_names = skin_names
        self.skin_names_chunks_queue = Queue()
        self.main_data = {}
        self.main_data_queue = Queue()
        self.api_url_path = "/price-aggregator/v1/aggregated-prices"

    #puts in queue
    def generate_chunks(self):
        for start in range(0,len(self.skin_names),80):
            names = self.skin_names[start:start+80]
            self.skin_names_chunks_queue.put({"names":names,"max_try":0})

    def generate_signature(self,secret_key,skin_names):
        nonce = str(round(time()))
        method = "GET"

        add = "&Titles=".join([r.utils.quote(name) for name in skin_names])
        add = f"?&Titles={add}&Limit=100"
        string_to_sign = method + self.api_url_path+ add + nonce
        signature_prefix = "dmar ed25519 "
        encoded = string_to_sign.encode('utf-8')
        secret_bytes = bytes.fromhex(secret_key)
        signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
        signature = signature_bytes[:64].hex()
        return {"nonce":nonce,"signature":signature,"signature_prefix":signature_prefix,"add":add}

    def parse_prices_from_returned_json(self,data):
        chunk = {}
        for each in data:
            self.main_data[each["MarketHashName"]] = {
                "best_offer": each["Offers"]["BestPrice"],
                "best_order": each["Orders"]["BestPrice"]
            }
            chunk[each["MarketHashName"]] = {
                "best_offer": each["Offers"]["BestPrice"],
                "best_order": each["Orders"]["BestPrice"]
            }
        self.main_data_queue.put(chunk)
    def dmarket_price_scrap(self,username,user_agent=None,max_try=3):
        if user_agent == None:
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        public_key = self.__api_keys[username]["public_key"]
        secret_key = self.__api_keys[username]["secret_key"]
        requests_exceptions = (r.exceptions.BaseHTTPError,r.exceptions.ChunkedEncodingError,r.exceptions.ConnectTimeout,r.exceptions.ConnectionError,r.exceptions.ContentDecodingError,r.exceptions.FileModeWarning,r.exceptions.HTTPError,r.exceptions.InvalidHeader,r.exceptions.InvalidProxyURL,r.exceptions.InvalidSchema,r.exceptions.InvalidURL,r.exceptions.MissingSchema,r.exceptions.ProxyError,r.exceptions.ReadTimeout,r.exceptions.RequestException,r.exceptions.RequestsDependencyWarning,r.exceptions.RequestsWarning,r.exceptions.RetryError,r.exceptions.SSLError,r.exceptions.StreamConsumedError,r.exceptions.Timeout,r.exceptions.TooManyRedirects,r.exceptions.URLRequired,r.exceptions.UnrewindableBodyError)
        while True:
            try:
                skin_names = self.skin_names_chunks_queue.get(False)
                signature = self.generate_signature(secret_key,skin_names["names"])

                headers = {
                    "X-Api-Key": public_key,
                    "X-Request-Sign": signature["signature_prefix"] + signature["signature"],
                    "X-Sign-Date": signature["nonce"],
                    "User-Agent":user_agent
                }

                resp = r.get(f"{self.url}{self.api_url_path}{signature['add']}", headers=headers,timeout=15)
                if resp.status_code == 200:
                    json_data = json.loads(resp.text)
                    if json_data["Error"] == None:
                        self.parse_prices_from_returned_json(json_data["AggregatedTitles"])
                        #print(len(json_data["AggregatedTitles"]),json_data["Total"],resp.headers["RateLimit-Remaining"])
                    else:
                        print(f"Dmarket: Returned json Error code not returned None: {json_data['Error']}")
                else:
                    print(f"Dmarket status code error: {resp.status_code}")
            except Empty:
                break
            except requests_exceptions:
                if max_try < skin_names["max_try"]:
                    skin_names["max_try"]+=1
                    self.skin_names_chunks_queue.put(skin_names)
            except Exception as e:
                print(f"Error during dmarket price scraping: {e}")
    def __del__(self):
        print(f"Total dmarket data: {len(self.main_data)}")
if __name__ == "__main__":
    file = open("/home/jagata/summerprojects/compare_skin_prices_steam/old_tests/get_item_names/item_names.txt","r")
    data = file.read().strip().split("====")
    file.close()

    api_keys = {
        "username1":{"public_key":"45425696b19e9ab58d98b6d5aad1b22863091b818c00b621838bb3eb87353151","secret_key":"821dadad93a511c30c03d01e7915792fc05fd31e305518b6d4894f275e8600fb45425696b19e9ab58d98b6d5aad1b22863091b818c00b621838bb3eb87353151"},
        "username2":{"public_key":"3542cf0882c132087b65420a50116de2a8d262e3a7679be0428d275a5fbc258d","secret_key":"564f6edf0b1044a36de2a5dcde4827e01e7fbf1dadecacbcaf86bac54a43b4d43542cf0882c132087b65420a50116de2a8d262e3a7679be0428d275a5fbc258d"},
        "username3":{"public_key":"ecb9798b9e85fb32edcbd479b7bcec40d2b3f2ec389dafd5c1a8b939cd1dd7dd","secret_key":"774b46760c813c099e264530d7cf6b2bf1893871d2594c52d083965ec8146a89ecb9798b9e85fb32edcbd479b7bcec40d2b3f2ec389dafd5c1a8b939cd1dd7dd"},
        "username4":{"public_key":"9603b1d1f25b89ec22351a3d7444e21b0f3cc625e16fe63c7013334e028d9a2c","secret_key":"31c34e95b1522dbbf4dd4259f0e06bbc09c69af32358c2a601fecca7df6caf3d9603b1d1f25b89ec22351a3d7444e21b0f3cc625e16fe63c7013334e028d9a2c"},
        "username5":{"public_key":"a2a9c37e1c55b7a52bae6aa9696744034c464ed497db0b1c11feba2b3578e43f","secret_key":"85687b0162d17f906c3434b6e6b59855a96c9a265b3db9eccc44eea96dc1bfefa2a9c37e1c55b7a52bae6aa9696744034c464ed497db0b1c11feba2b3578e43f"},
        "username6":{"public_key":"c2a48857184046bcfbc1ff3c746465e56e2b7a5d1ee734480287c6cb69a724f7","secret_key":"fe81bae7c37fad5431302fd015341c29c4653766feab118952240ef9c2f497bfc2a48857184046bcfbc1ff3c746465e56e2b7a5d1ee734480287c6cb69a724f7"},
        "username7":{"public_key":"71c65554aa762d365c0b839d313c7aadca2d74800a1c94af3fe2709ecfbeee19","secret_key":"2790463e9c04c9f5952185728a16b00739c26ce0b22a71d2a56fe09edbf22a4e71c65554aa762d365c0b839d313c7aadca2d74800a1c94af3fe2709ecfbeee19"},
        "username8":{"public_key":"1ddf9a078fa91a868ee5936cb4e6fe608e65ba008b25bada3a55281018cd2b24","secret_key":"49371aa6d656966b95d94ff91ac2163417ad42dd97f0c49047293823feee1ea71ddf9a078fa91a868ee5936cb4e6fe608e65ba008b25bada3a55281018cd2b24"}
    }
    import threading
    dmarket_scrap = Dmarket_scrap("https://api.dmarket.com",api_keys,data)
    dmarket_scrap.generate_chunks()

    for username in list(api_keys.keys())[:2]:
        print("start")
        for _ in range(4):
            threading.Thread(target=dmarket_scrap.dmarket_price_scrap, args=(username,)).start()












#
