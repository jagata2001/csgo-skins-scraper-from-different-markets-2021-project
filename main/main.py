from itertools import cycle
import threading
from queue import Empty,Queue
import time
from random import randint

from classes.proxy_classes.scrap_proxy_class import Scrap_proxy
from classes.proxy_classes.proxy_checker_class import Proxy_checker
from classes.steam_classes.steam_login_class import Steam_login
from classes.database_classes.database_proxy_class import Database_proxy
from classes.static_methods_class import Static_methods
from classes.steam_classes.steam_market_scrap_class import Steam_market_scrap
from classes.market_csgo_classes.market_csgo_scrap_class import Market_csgo_scrap
from classes.database_classes.database_skin_class import Database_skin
from classes.dmarket_classes.dmarket_price_scrap_class import Dmarket_scrap

######################




######################


##################################
#       START FIRST LOGIN        #
##################################

steam_users_data = {
 "qweq123127":{"username":"qweq123127","password":"liloton286@186site.com","try_count":0},
 "weqwe23211":{"username":"weqwe23211","password":"mipela9432@186site.com","try_count":0},
 "bbasd23":{"username":"bbasd23","password":"sebomof897@100xbit.com","try_count":0}
}
max_try = 3
steam_cookies = {}
for each in list(steam_users_data.keys()):
    each = steam_users_data[each]
    while each["try_count"]<max_try:
        steam_login = Steam_login(each["username"],each["password"])
        first_load = steam_login.get_first_cookies()
        if first_load:
            rsa_key = steam_login.get_rsa_key()
            if rsa_key:
                login_resp = steam_login.do_login()
                if login_resp:
                    print(f"user: {each['username']} Succesfully loged in...")
                    steam_cookies[each["username"]] = steam_login.cookies
                    each["try_count"] = 0
                    break
                elif login_resp == 0:
                    break
        each["try_count"]+=1

if len(steam_cookies) == 0:
    print("\n\n\n")
    exit("Somethin went wrong Cookie dict is empty")

##################################
#        END FIRST LOGIN         #
##################################
print(steam_users_data)
##################################
#      START PROXY SCRAPING     #
##################################
def proxy_scrap_main():
    while True:
        print(f"Scraping proxy...")
        #first argument is proxy api url, second argument is limit for getting proxy quantity per page load
        proxy_scraper = Scrap_proxy("https://proxylist.geonode.com/api/proxy-list",100)
        #first argument is for maximum try for loading proxy, second is for limitation of proxy quantity
        proxy_scraper.get_all_proxy_data_from_returned_json(3)

        #first argument is giving scrapped proxy data,second is url on which we will test the proxy
        proxy_checker = Proxy_checker(proxy_scraper.proxy_data,"https://steamcommunity.com/market/search/render/?query=&start=1&count=1&search_descriptions=0&sort_column=popular&sort_dir=desc&appid=730")
        #removes duplicate proxies from passed data in order avoid time waste
        proxy_checker.clean_from_duplicate_data()
        #prepares cleaned data for checking
        proxy_checker.prepare_for_check()
        #checking proxies
        for _ in range(50):
            threading.Thread(target=proxy_checker.check_proxy, name="Proxy checker").start()
        #sleep until proxy will become checked
        while Static_methods.thread_exists("Proxy checker"):
            #print(f"left: {proxy_checker.proxies_queue.qsize()}")
            time.sleep(1)
        print(proxy_checker)
        print(f"End scraping...")
        time.sleep(30)


main_proxy_scraper_thread = threading.Thread(target=proxy_scrap_main,name="Main (Proxy)",daemon=True).start()

##################################
#       END PROXY SCRAPING      #
##################################


proxy_db = Database_proxy("jagata","password","steam_skin_data")
#for wait proxy db to filled
while proxy_db.count_proxy() < 1000:
    time.sleep(2)
proxy_db.close()


##################################
#  START STEAM MARKET SCRAPING  #
##################################

def steam_main():
    ###################################
    #            FUNCTIONS            #
    ###################################
    def relogin(user_data,max_try):
        login_done = False
        while user_data["try_count"]<max_try:
            steam_login = Steam_login(user_data["username"],user_data["password"])
            first_load = steam_login.get_first_cookies()
            if first_load:
                rsa_key = steam_login.get_rsa_key()
                if rsa_key:
                    login_resp = steam_login.do_login()
                    if login_resp:
                        print(f"user: {user_data['username']} Succesfully relogged in")
                        login_done = steam_login.cookies
                        user_data["try_count"] = 0
                        break
                    elif login_resp == 0:
                        break
            user_data["try_count"]+=1
        return login_done

    def check_returned_data(steam_scraper,thread_quantity):
        relogged_in_usernames = []
        run_thread_list = []
        while True:
            try:
                data = steam_scraper.return_data.get(False)
                run_thread = False
                if data["relogin"] and data["status"] == False:
                    #requires relogin
                    if relogged_in_usernames.count(data['username']) == 0:
                        print(f"User: {data['username']} logged out")
                        print("trying relogin.....")
                        max_try = 5
                        user_data = steam_users_data[data["username"]]
                        login_done = relogin(user_data,max_try)
                        relogged_in_usernames.append(data['username'])
                        if login_done != False:
                            steam_scraper.cookies_dict[user_data["username"]] = login_done
                            steam_cookies[user_data["username"]] = login_done
                            run_thread = True
                        else:
                            steam_scraper.cookies_dict.pop(user_data["username"],None)
                            steam_cookies.pop(user_data["username"],None)
                            if len(steam_scraper.cookies_dict) == 0:
                                break
                    else:
                        if list(steam_scraper.cookies_dict.keys()).count(data["username"]) == 1:
                            run_thread = True
                elif data["relogin"] == False and data["status"] == None:
                    if list(steam_scraper.cookies_dict.keys()).count(data["username"]) == 1:
                        run_thread = True
                    if run_thread:
                        run_thread_list.append(data["username"])
            except Empty:
                return run_thread_list
            time.sleep(0.5)



    def insert_skin_price_worker(steam_scraper):
        skin_db = Database_skin("jagata","password","steam_skin_data")
        break_loop = False
        while True:
            try:
                if Static_methods.thread_exists("Steam market") == False:
                    break_loop = True
                collected_data = steam_scraper.main_data_queue.get(False)
                insert_data = Static_methods.prepare_market_prices_to_insert_into_database(collected_data)
                skin_db.insert_skin_data_from_steam_market(insert_data,"offer")
            except Empty:
                if Static_methods.thread_exists("Steam market") == True:
                    time.sleep(2)
                    continue
                if break_loop == True:
                    skin_db.close()
                    break
    ###################################
    #         END OF FUNCTIONS        #
    ###################################
    steam_cookies = {"qweq123127":{'sessionid': '21f5a9452643172655707b43', 'steamCountry': 'GE%7C57e12a74c5d4dff94d8bb91ec934f957', 'steamLoginSecure': '76561199196453864%7C%7C2D4810EE4C94CE92E8B955B70B91569BA6BFFF82'}
    }
    while True:
        print("Scraping market prices...")
        proxy_db = Database_proxy("jagata","password","steam_skin_data")
        #first argument is proxy limit default is 5000
        proxy_data = proxy_db.select_proxy_for_steam_market()
        #it creates proxies pool for use in scraping
        proxy_pool = Static_methods.create_proxy_pool(proxy_data)
        proxy_db.close()
        if len(proxy_data) <= 200:
            print("Not enough proxies. please wait...")
            time.sleep(150)
            continue



        #steam market scraper. first argument is steam game id,
        #second steam user's cookie,
        #therd proxy pool that is required for avoid blocking from steam
        Steam_scraper = Steam_market_scrap(730,steam_cookies,proxy_pool)

        #getting steam skin quantity for provided steam game id
        for _ in range(4):
            func_resp = Steam_scraper.get_skin_quantity()
            returned_data = Steam_scraper.return_data.get()
            if func_resp == True:
                break
            elif func_resp == False:
                continue
            else:
                if returned_data["relogin"] and returned_data["status"] == False:
                    print(f"User: {returned_data['username']} logged out")
                    print("trying relogin.....")
                    #requires relogin
                    max_try = 5
                    user_data = steam_users_data[returned_data["username"]]
                    login_done = relogin(user_data,max_try)
                    if login_done != False:
                        Steam_scraper.cookies_dict[user_data["username"]] = login_done
                        steam_cookies[user_data["username"]] = login_done
                        func_resp = Steam_scraper.get_skin_quantity()
                        returned_data = Steam_scraper.return_data.get()

                        break
                    else:
                        Steam_scraper.cookies_dict.pop(user_data["username"],None)
                        steam_cookies.pop(user_data["username"],None)
                        if len(Steam_scraper.cookies_dict) == 0:
                            print("Steam scraper cookies dict have become empty.")
                            exit()
                else:
                    continue

        #checking if Steam scraper get skin quantity worked correctly
        if Steam_scraper.start_from.qsize() == 0:
            print("Start from queue size is 0 Steam market have to continue loop")
            time.sleep(30)
            continue

        #threads quantitiy for Steam market
        market_price_scrap_thread_quantity = 12
        for_iter = cycle(list(Steam_scraper.cookies_dict.keys()))
        user_name_list_for_thread_run = [next(for_iter) for _ in range(market_price_scrap_thread_quantity)]
        for username in user_name_list_for_thread_run:
            threading.Thread(target=Steam_scraper.steam_price_scrap,name="Steam market",args=(username,)).start()

        #contains usernames of users
        cdata = check_returned_data(Steam_scraper,market_price_scrap_thread_quantity)

        #check if cookie dict becomes empty
        if len(Steam_scraper.cookies_dict) == 0:
            print("Steam scraper cookies dict have become empty.")
            exit()
        #rerun stopped threads
        for username in cdata:
            print("Some steam market thread died so requires to rerun")
            if list(Steam_scraper.cookies_dict.keys()).count(username) == 1:
                threading.Thread(target=Steam_scraper.steam_price_scrap,name="Steam market",args=(username,)).start()

        for _ in range(24):
            threading.Thread(target=insert_skin_price_worker,args=(Steam_scraper,),name="Insert worker").start()


        while Static_methods.thread_exists("Insert worker") or Static_methods.thread_exists("Steam market"):
            time.sleep(5)
            print(f"main_data_queue qsize:{Steam_scraper.main_data_queue.qsize()} main_data: {len(Steam_scraper.main_data)} proxies left: {Steam_scraper.proxy_pool.qsize()} pages left: {Steam_scraper.start_from.qsize()}")
        print(f"steam market returned results sum: {sum(Steam_scraper.deletethis)}")

        print("Succesfully inserted...")
        print("End Steam market scraping...")
        print("\n\n")
        time.sleep(10)
##################################
#   END STEAM MARKET SCRAPING    #
##################################



##################################
#   START MARKET CSGO SCRAPING   #
##################################

def market_csgo_main():
    ###################################
    #            FUNCTIONS            #
    ###################################
    def insert_skin_price_worker_market_csgo(data_queue):
        skin_db = Database_skin("jagata","password","steam_skin_data")
        break_loop = False
        while True:
            try:
                insert_data = data_queue.get(False)
                skin_db.insert_skin_data_from_market_csgo(insert_data,"offer")
            except Empty:
                skin_db.close()
                break

    ###################################
    #         END OF FUNCTIONS        #
    ###################################
    old_timestamp = None
    while True:
        market_csgo = Market_csgo_scrap("https://market.csgo.com/api/v2/prices/USD.json")
        market_csgo_data = market_csgo.market_csgo_skin_price_scrap(5)

        if market_csgo_data["data"] != None and market_csgo_data["timestamp"] != old_timestamp:
            print("Scraping market csgo prices...")

            insert_data = Static_methods.prepare_market_prices_to_insert_into_database(market_csgo_data["data"])

            insert_data_queue = Queue()
            for start in range(0,len(insert_data),100):
                insert_data_queue.put(insert_data[start:start+100])
            for _ in range(24):
                threading.Thread(target=insert_skin_price_worker_market_csgo,args=(insert_data_queue,),name="Market csgo Insert worker").start()
            while Static_methods.thread_exists("Market csgo Insert worker"):
                time.sleep(1)

            print(f"Market csgo data Successfully inserted. timestamp: {market_csgo_data['timestamp']}")
            old_timestamp = market_csgo_data["timestamp"]
            time.sleep(10)

        time.sleep(5)


##################################
#    END MARKET CSGO SCRAPING    #
##################################

##################################
#     START DMARKET SCRAPING     #
##################################

def dmarket_main():
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
    ###################################
    #            FUNCTIONS            #
    ###################################
    def insert_skin_price_from_dmarket(dmarket_scrap):
        skin_db = Database_skin("jagata","password","steam_skin_data")
        break_loop = False
        while True:
            try:
                if Static_methods.thread_exists("Dmarket") == False:
                    break_loop = True
                collected_data = dmarket_scrap.main_data_queue.get(False)
                insert_data = Static_methods.prepare_dmarket_prices_to_insert_into_database(collected_data)
                skin_db.insert_skin_data_from_dmarket(insert_data)
            except Empty:
                if Static_methods.thread_exists("Dmarket") == True:
                    time.sleep(2)
                    continue
                if break_loop == True:
                    skin_db.close()
                    break
    ###################################
    #         END OF FUNCTIONS        #
    ###################################
    while True:
        print("Start dmarket scraping...")
        skin_db_for_skin_names = Database_skin("jagata","password","steam_skin_data")
        skin_names = skin_db_for_skin_names.select_all_skin_names()
        skin_db_for_skin_names.close()

        dmarket_scrap = Dmarket_scrap("https://api.dmarket.com",api_keys,skin_names)
        dmarket_scrap.generate_chunks()

        user_name_list_for_thread_run = []

        #(dmarket_price_scrap_thread_quantity/max_threads_per_user)>= len(list(api_keys).keys()) maximum value
        #len(list(api_keys).keys())*max_threads_per_user>=dmarket_price_scrap_thread_quantity maximum value

        dmarket_price_scrap_thread_quantity = 12
        max_threads_per_user = 4
        exit_from_loop = False
        iter_add = randint(0,len(list(api_keys.keys()))-int(dmarket_price_scrap_thread_quantity/max_threads_per_user))
        for i in range(0,dmarket_price_scrap_thread_quantity,max_threads_per_user):
            itr = int(((i+max_threads_per_user)/max_threads_per_user)-1)+iter_add
            for _ in range(max_threads_per_user):
                if len(user_name_list_for_thread_run) < dmarket_price_scrap_thread_quantity:
                    user_name_list_for_thread_run.append(list(api_keys.keys())[itr])
                else:
                    exit_from_loop = True
                    break
            if exit_from_loop == True:
                break

        for username in user_name_list_for_thread_run:
                threading.Thread(target=dmarket_scrap.dmarket_price_scrap, args=(username,),name="Dmarket").start()

        for _ in range(24):
            threading.Thread(target=insert_skin_price_from_dmarket,args=(dmarket_scrap,),name="Dmarket insert worker").start()

        while Static_methods.thread_exists("Dmarket") or Static_methods.thread_exists("Dmarket insert worker"):
            print(f"Dmarket Chunks left: {dmarket_scrap.skin_names_chunks_queue.qsize()} loaded data:{dmarket_scrap.main_data_queue.qsize()}")
            time.sleep(5)
        print("Successfully inserted dmarket data")
        time.sleep(60)
##################################
#      END DMARKET SCRAPING      #
##################################
threading.Thread(target=steam_main,name="Main (Steam)",daemon=True).start()
threading.Thread(target=market_csgo_main,name="Main (Market csgo)",daemon=True).start()
threading.Thread(target=dmarket_main,name="Main (Dmarket)",daemon=True).start()


while Static_methods.thread_exists("Main (Steam)") and Static_methods.thread_exists("Main (Market csgo)") and Static_methods.thread_exists("Main (Dmarket)") and Static_methods.thread_exists("Main (Proxy)"):
    time.sleep(5)
print(f"exit from here")
print(Static_methods.thread_exists("Main (Steam)"), Static_methods.thread_exists("Main (Market csgo)"), Static_methods.thread_exists("Main (Dmarket)"), Static_methods.thread_exists("Main (Proxy)"))











#######################################
#          CREATED BY jagata          #
#######################################
