from classes.buff_163_classes.buff_163_login_class import Buff163_login
from classes.buff_163_classes.buff_163_market_scrap_class import Buff163_scrap
from classes.static_methods_class import Static_methods
from classes.database_classes.database_proxy_class import Database_proxy


import threading
phone_number = "phone number"

buff = Buff163_login(phone_number,"password")#,'GE'
print("first page laoding...")
buff.load()

print("trying to login...")
status = buff.login()
print(status)

#status = {'status': True, 'message': 'successfully logged in', 'cookies': [{'domain': '.163.com', 'httpOnly': True, 'name': 'NTES_YD_SESS', 'path': '/', 'secure': False, 'value': 'uWkqFRVNiu0JvB3b4dr0eC7uueuiUoCLhhilT0C7JkI7BsDT0KUqAAn1d6BTUGm0f.iqmrtc40MCOPYdzEH_JOCN31GuppRSIRdf61.SKLrG0YWF1I9ej5O05Tb3DLIPckCywWjfXrNsezsTFMR7lS8WxPRLwe7a_KHf41FzWnbv6aHBth8BZT_SfIBUBEpXpwiXkr3XwxRU.LBnAV40X_dFr47LIX0ONEBevkBpDoCEi'}, {'domain': 'buff.163.com', 'httpOnly': True, 'name': 'session', 'path': '/', 'secure': False, 'value': '1-kZEMae9Zmb9uUcWhB1iQTWUI2D-Hyi1ncknx5oCbqUPH2039213738'}, {'domain': '.163.com', 'expiry': 1660995637, 'httpOnly': False, 'name': 'P_INFO', 'path': '/', 'secure': False, 'value': '995-5776*****|1629502837|1|netease_buff|00&99|GE&1629502716&netease_buff#GE&null#10#0#0|&0|null|995-5776*****'}, {'domain': '.163.com', 'httpOnly': False, 'name': 'S_INFO', 'path': '/', 'secure': False, 'value': '1629502837|0|3&80##|995-5776*****'}, {'domain': 'buff.163.com', 'expiry': 4733424000, 'httpOnly': False, 'name': 'Device-Id', 'path': '/', 'secure': False, 'value': '4LG87Ev1XPbgO82i2BpY'}, {'domain': 'buff.163.com', 'httpOnly': False, 'name': 'Locale-Supported', 'path': '/', 'secure': False, 'value': 'en'}, {'domain': '.163.com', 'expiry': 1692574840, 'httpOnly': False, 'name': '_ga', 'path': '/', 'secure': False, 'value': 'GA1.2.2134193151.1629502802'}, {'domain': '.163.com', 'expiry': 1629589240, 'httpOnly': False, 'name': '_gid', 'path': '/', 'secure': False, 'value': 'GA1.2.1871196072.1629502802'}, {'domain': 'buff.163.com', 'httpOnly': False, 'name': 'game', 'path': '/', 'secure': False, 'value': 'csgo'}, {'domain': 'buff.163.com', 'httpOnly': False, 'name': 'csrf_token', 'path': '/', 'secure': False, 'value': 'IjdhMzhjMzNkY2I1ZWRmNTMwMWQ5ODQzZThmZDVjOWQwNGFlMDllZDgi.FAHO-A.JqlALugNIiX67Al-KNp5a5O0xZQ'}, {'domain': 'buff.163.com', 'expiry': 1630395639, 'httpOnly': True, 'name': 'remember_me', 'path': '/', 'secure': False, 'value': 'U1095070194|39eT5LpBbAk5Ib4gSXjiB6DKzpANPlaM'}, {'domain': '.163.com', 'expiry': 1629502861, 'httpOnly': False, 'name': '_gat_gtag_UA_109989484_1', 'path': '/', 'secure': False, 'value': '1'}]}
cookies = {}
import requests as r

if status["status"]:
    cookies[phone_number] = Static_methods.prepare_buff_163_cookies(status["cookies"])

else:
    print(status["message"])

print("Scraping market scraping...")
proxy_db = Database_proxy("jagata","password","steam_skin_data")
#first argument is proxy limit default is 5000
proxy_data = proxy_db.select_proxy_for_steam_market()
#it creates proxies pool for use in scraping
proxy_pool = Static_methods.create_proxy_pool(proxy_data)
proxy_db.close()

buff163_scrap = Buff163_scrap("csgo",cookies,proxy_pool)
status = buff163_scrap.get_page_quantity()
if status == True:
    buff163_scrap.return_data.get()
    print("start buff scraping")
    for _ in range(12):
        threading.Thread(target=buff163_scrap.buff_163_market_price_scrap,args=(phone_number,),name="buff").start()
    #buff163_scrap.buff_163_market_price_scrap(phone_number)
    import time
    time.sleep(5)
    print(buff163_scrap.main_data)
    while Static_methods.thread_exists("buff"):
        print(f"data: {len(buff163_scrap.main_data)}")
        time.sleep(0.5)
