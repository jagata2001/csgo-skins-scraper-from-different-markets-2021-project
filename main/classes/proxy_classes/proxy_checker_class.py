from classes.static_methods_class import Static_methods
from classes.database_classes.database_proxy_class import Database_proxy

from queue import Queue,Empty
import requests as r
from datetime import datetime
import json
from sys import exit


class Proxy_checker:
    def __init__(self,proxy_data,test_url):
        self.proxy_data = proxy_data
        self.test_url = test_url
        self.cleanned_proxy_data = {}
        self.proxies_queue = Queue()
        self.inserted_count = 0


    def clean_from_duplicate_data(self):
        for each in self.proxy_data:
            self.cleanned_proxy_data[each["ip"]] = {
                                                    "port":each["port"],
                                                    "protocol":each['protocols'][0]
                                                    }
    def prepare_for_check(self):
        for ip,data in self.cleanned_proxy_data.items():
            self.proxies_queue.put(
                                    {
                                        "ip": ip,
                                        "port":data["port"],
                                        "protocol":data["protocol"]
                                    }
                                  )
    def check_proxy(self):
        db = Database_proxy("jagata","678946icom","steam_skin_data")
        requests_exceptions = (r.exceptions.BaseHTTPError,r.exceptions.ChunkedEncodingError,r.exceptions.ConnectTimeout,r.exceptions.ConnectionError,r.exceptions.ContentDecodingError,r.exceptions.FileModeWarning,r.exceptions.HTTPError,r.exceptions.InvalidHeader,r.exceptions.InvalidProxyURL,r.exceptions.InvalidSchema,r.exceptions.InvalidURL,r.exceptions.MissingSchema,r.exceptions.ProxyError,r.exceptions.ReadTimeout,r.exceptions.RequestException,r.exceptions.RequestsDependencyWarning,r.exceptions.RequestsWarning,r.exceptions.RetryError,r.exceptions.SSLError,r.exceptions.StreamConsumedError,r.exceptions.Timeout,r.exceptions.TooManyRedirects,r.exceptions.URLRequired,r.exceptions.UnrewindableBodyError)
        checked_proxy = []
        while True:
            try:
                pr_data =  self.proxies_queue.get(False)
                proxies = {
                    "http":f"{pr_data['protocol']}://{pr_data['ip']}:{pr_data['port']}",
                    "https":f"{pr_data['protocol']}://{pr_data['ip']}:{pr_data['port']}"
                }
                resp = r.get(self.test_url,proxies=proxies,timeout=5)
                if resp.status_code == 200:
                    resp_data = json.loads(resp.text)
                    if resp_data["success"]:
                        pr_data["check_time"] = datetime.now()
                        pr_data["server_response_time"] = resp.elapsed.total_seconds()
                        checked_proxy.append(pr_data)
            except KeyboardInterrupt:
                exit("Exit by Keyboard")
            except requests_exceptions as err:
                pass
            except Empty:
                if len(checked_proxy)>0:
                    prepared_data = Static_methods.prepare_proxy_to_insert_into_database(checked_proxy)
                    ret_data = db.insert_proxy_data_into_database(prepared_data)
                    self.inserted_count+=ret_data
                db.close()
                break
            except Exception as e:
                print(f"Something went wrong proxy checker class function proxy_check error: {e}")

            if len(checked_proxy)>=10:
                prepared_data = Static_methods.prepare_proxy_to_insert_into_database(checked_proxy)
                ret_data = db.insert_proxy_data_into_database(prepared_data)
                checked_proxy = []
                self.inserted_count+=ret_data

    def __repr__(self):
        return f"Total inserted proxy {self.inserted_count}"








#
