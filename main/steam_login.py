from itertools import cycle
import threading
from queue import Empty
import time

from classes.proxy_classes.scrap_proxy_class import Scrap_proxy
from classes.proxy_classes.proxy_checker_class import Proxy_checker
from classes.steam_classes.steam_login_class import Steam_login
from classes.database_classes.database_proxy_class import Database_proxy
from classes.static_methods_class import Static_methods
from classes.steam_classes.steam_market_scrap_class import Steam_market_scrap
from classes.market_csgo_classes.market_csgo_scrap_class import Market_csgo_scrap
from classes.database_classes.database_skin_class import Database_skin

######################
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
cookies = {}
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
                    cookies[each["username"]] = steam_login.cookies
                    each["try_count"] = 0
                    break
                elif login_resp == 0:
                    break
        each["try_count"]+=1

if len(cookies) == 0:
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
        proxy_scraper = Scrap_proxy("https://proxylist.geonode.com/api/proxy-list",1000)
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
            time.sleep(1)
        print(proxy_checker)
        print(f"End scraping...")
        #sleep for 5 minute
        time.sleep(300)


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

def steam_market_scrap():
    while True:
        print("Scraping market scraping...")
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

        #cookies = {"qweq123127":{'sessionid': 'a369e9b4e4cec8ea607f8655', 'steamCountry': 'GE%7C57e12a74c5d4dff94d8bb91ec934f957', 'steamLoginSecure': '76561199023391720%7C%7CFB39E8FE0D45262338642D57DFEE7637304A2A75'}
        #}

        #steam market scraper. first argument is steam game id,
        #second steam user's cookie,
        #therd proxy pool that is required for avoid blocking from steam
        Steam_scraper = Steam_market_scrap(730,cookies,proxy_pool)

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
                        func_resp = Steam_scraper.get_skin_quantity()
                        returned_data = Steam_scraper.return_data.get()
                        break
                    else:
                        Steam_scraper.cookies_dict.pop(user_data["username"],None)
                        if len(Steam_scraper.cookies_dict) == 0:
                            exit("Steam scraper cookies dict have become empty.")
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

        ###################################
        #            FUNCTIONS            #
        ###################################
        def check_returned_data(thread_quantity):
            relogged_in_usernames = []
            run_thread_list = []
            while True:
                try:
                    data = Steam_scraper.return_data.get(False)
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
                                Steam_scraper.cookies_dict[user_data["username"]] = login_done
                                run_thread = True
                            else:
                                Steam_scraper.cookies_dict.pop(user_data["username"],None)
                                if len(Steam_scraper.cookies_dict) == 0:
                                    break
                        else:
                            if list(Steam_scraper.cookies_dict.keys()).count(data["username"]) == 1:
                                run_thread = True
                    elif data["relogin"] == False and data["status"] == None:
                        if list(Steam_scraper.cookies_dict.keys()).count(data["username"]) == 1:
                            run_thread = True

                    if run_thread:
                        run_thread_list.append(data["username"])

                except Empty:
                    return run_thread_list
                time.sleep(0.5)

        def insert_skin_price_worker(data):
            skin_db = Database_skin("jagata","password","steam_skin_data")
            while True:
                try:
                    skin_insert_data = data.get(False)
                    skin_db.insert_skin_data_into_database(skin_insert_data)
                except Empty:
                    skin_db.close()
                    break
        ###################################
        #         END OF FUNCTIONS        #
        ###################################

        #contains usernames of users
        cdata = check_returned_data(market_price_scrap_thread_quantity)
        #rerun stopped threads
        for username in cdata:
            print("Some steam market thread died so requires to rerun")
            if list(Steam_scraper.cookies_dict.keys()).count(username) == 1:
                threading.Thread(target=Steam_scraper.steam_price_scrap,name="Steam market",args=(username,)).start()

        while Static_methods.thread_exists("Steam market"):
            time.sleep(5)
            print(f"skin name qsize:{Steam_scraper.skin_names_for_market_csgo.qsize()} main_data: {len(Steam_scraper.main_data)} proxies left: {Steam_scraper.proxy_pool.qsize()} pages left: {Steam_scraper.start_from.qsize()}")


        print(f"steam market returned results sum: {sum(Steam_scraper.deletethis)}")
        print("Scraping market csgo prices..")
        market_csgo = Market_csgo_scrap("https://market.csgo.com/api/v2/prices/USD.json")
        market_csgo_data = market_csgo.market_csgo_skin_price_scrap(5)
        print("prices from steam and market csgo are scapped")

        if market_csgo_data != None:
            print("Start inserting...")
            #returns queue
            skin_insert_data = Static_methods.prepare_market_prices_to_insert_into_database(Steam_scraper.main_data,market_csgo_data)
            for _ in range(24):
                threading.Thread(target=insert_skin_price_worker,args=(skin_insert_data,),name="Insert worker").start()


        while Static_methods.thread_exists("Insert worker"):
            time.sleep(1)
        print("Succesfully inserted...")
        print("End market scraping...")
        print("\n\n")
        time.sleep(10)

threading.Thread(target=steam_market_scrap,name="Main (Steam)",daemon=True).start()


while Static_methods.thread_exists("Main (Steam)") and Static_methods.thread_exists("Main (Proxy)"):
    time.sleep(5)

##################################
#   END STEAM MARKET SCRAPING   #
##################################













#######################################
#          CREATED BY jagata          #
#######################################
