import requests as r
import json

class Market_csgo_scrap:
    def __init__(self,api_url):
        self.api_url = api_url
    def process_data(self,json_data):
        data = {}
        for each in json_data:
            data[each["market_hash_name"]] = {"best_offer":float(each["price"])}
        return data

    def market_csgo_skin_price_scrap(self,max_try=3):
        headers = {
            'authority': 'market.csgo.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',

        }
        for _ in range(max_try):
            try:
                resp = r.get(self.api_url)
                if resp.status_code == 200:
                    json_data = json.loads(resp.text)
                    if json_data["success"] == True:
                        data = self.process_data(json_data["items"])
                        return {"data":data,"timestamp":json_data["time"]}
            except Exception as e:
                print(f"Error during market csgo scrapping: {e}")
