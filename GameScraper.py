from sys import exit as sys_exit
from fake_useragent import UserAgent
from time import sleep
from bs4 import BeautifulSoup as bs
import html5lib
from selenium import webdriver
from pandas import DataFrame
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager
from requests import get, Session
from os import environ
from os.path import join as join_path
def debug(t):print(t);input("<press enter>")
class LittleGamingGeek:
    # gamestop https://www.gamestop.com/video-games
    # pricegrabber https://www.pricegrabber.com/videogames1/browse/
    # steam https://store.steampowered.com/search/?filter=topsellers&os=win
    gaming_information_web_sites = {"metacritic":{"main_url":"https://www.metacritic.com", "filtered":False},
                                    "gamespot":{"main_url":"https://www.gamespot.com", "filtered":False},
                                    "ign":{"main_url":"https://www.ign.com", "filtered":False},
                                    "pricegrabber":{"main_url":"https://www.pricegrabber.com", "filtered":False}
                                    }
    useragent = UserAgent()
    s = Session()
    s.headers.update({"User-Agent":useragent.random})
    #s.verify = False
    def __init__(self):
        # Verifica que las paginas no esten filtradas por fortinet en caso de utilizar el internet de la uni
        def mark_filtered(web_name):
            LittleGamingGeek.gaming_information_web_sites[web_name]["filtered"] = True
        for web_name, web_info in LittleGamingGeek.gaming_information_web_sites.copy().items():
            for field, value in web_info.items():
                if field == "main_url":
                    try:
                        r = LittleGamingGeek.s.get(value)
                    except:
                        mark_filtered(web_name=web_name)
                    else:
                        if r.status_code == 404 or r.status_code == 403: mark_filtered(web_name=web_name)
                    finally:
                        if r: r.close()
        validation = [i["filtered"] for i in LittleGamingGeek.gaming_information_web_sites.copy().values()]
        if all(validation):
            print("All the web pages are filtered")
            sys_exit(1)
        else:
            print(f"Available {validation.count(False)} of {len(validation)}")
            for available, info in LittleGamingGeek.gaming_information_web_sites.copy().items():
                if not info["filtered"]: print(available, info["main_url"])
        self.metacritic_bot = self.metacritic(LittleGamingGeek.gaming_information_web_sites["metacritic"]["main_url"])
        #self.pricegrabber_bot = self.PriceGrabber(LittleGamingGeek.gaming_information_web_sites["pricegrabber"]["main_url"])

    class metacritic:
        # Metacritic obtiene nombre de juegos, fecha de lanzamiento y evaluacion de los jugadores
        # metacritic no obtiene los precios por si solo, se utilizara en conjunto con pricegrabber, amazon o google shopping
        data = {
            "gamename": [],
            "platform": [],
            "releasedate": [],
            "metarating": [],
            "userrating": [],
            "developer": [],
            "publisher": [],
            "genre": []
        }
        def __init__(self, main_url):
                self.main_url = main_url
                options = webdriver.ChromeOptions()
                #options.add_argument("--headless")
                options.add_argument(f"--useragent={LittleGamingGeek.useragent.random}")
                self.browser = webdriver.Chrome(options=options)

        def scrap(self, limit=3):
            scrap_url = self.main_url + "/browse/game"
            scrap_url = f"{scrap_url}/?releaseYearMin={self.filterDate[0]}&releaseMaxYear={self.filterDate[1]}"
            for platform, filter in self.filters.items():
                if filter["selected"] == True:
                    scrap_url += filter["added_url"]
            self.browser.get(scrap_url + "&page=1")
            try:
                pageLimits = bs(self.browser.page_source, "html5lib").find_all("span", {"class":"c-navigationPagination_itemButtonContent u-flexbox u-flexbox-alignCenter u-flexbox-justifyCenter"})
            except:
                print("No results found for this filter combination")
            else:
                max_found = 0
                for page_number in pageLimits:
                    try:
                        testing = page_number.get_text().strip()
                        testing = int(testing)
                    except:
                        continue
                    else:
                        max_found = testing if testing > max_found else max_found
                if max_found > 0:
                    if not limit:
                        for i in range(1, max_found + 1):
                            self.add_game(scrap_url + f"&page={i}")
                    else:
                        if limit > max_found:
                            limit = pageLimit
                        for i in range(1, limit + 1):
                            self.add_game(scrap_url + f"&page={i}")
                else:
                    print("No results...")

        def add_game(self, url):
            def getInformation(blockinfo):
                for productInfo in blockinfo:
                    game_name_span = productInfo.find("div", {"class": "c-finderProductCard_title"}).find_all("span")[1]
                    game_name = game_name_span.get_text(strip=True) if game_name_span else "N/A"
                    #debug(game_name)
                    game_date_span = productInfo.find("div", {"class": "c-finderProductCard_meta"}).find_all("span")[0]
                    game_date = game_date_span.get_text(strip=True) if game_name_span else "N/A"
                    game_rating_span = productInfo.find("span",{"class": "c-finderProductCard_metaItem c-finderProductCard_score"}).find_all("span")[0]
                    game_rating = game_rating_span.get_text(strip=True) if game_name_span else "N/A"
                    gameDetails = productInfo.find("a", {"class": "c-finderProductCard_container g-color-gray80 u-grid"})["href"]
                    rating = []
                    if gameDetails:
                        self.browser.get(self.main_url + gameDetails)
                        ratings = bs(self.browser.page_source, "html5lib").find_all("div", {"class": "c-productScoreInfo_scoreContent u-flexbox u-flexbox-alignCenter u-flexbox-justifyFlexEnd g-width-100 u-flexbox-nowrap"})
                        for i in ratings:
                            r = i.find("span", {"data-v-4cdca868": True}).get_text()
                            rating.append(r) if r else rating.append("N/A")
                        # get plublisher, developer, platform release date, original and gender
                        self.browser.get(self.main_url + gameDetails + "details")
                        current_game_info_html_bs_filtrable = bs(self.browser.page_source, "html5lib")
                        g_platform = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_sectionContainer u-flexbox u-flexbox-column"}).find_all("li")
                        g_platform_concatenated = []
                        for p in g_platform:
                            g_platform_concatenated.append(p.get_text().strip())
                        g_platform_concatenated = ",".join(g_platform_concatenated)
                        developer_li = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_Developer u-flexbox u-flexbox-row"}).find_all("li")
                        developers = []
                        for li in developer_li:
                            developer = li.get_text().strip()
                            if developer:
                                developers.append(developer)
                        developers = ",".join(developers)
                        try:
                            publisher = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_Distributor u-flexbox u-flexbox-row"}).find("span", {"class": "c-gameDetails_Distributor u-flexbox u-flexbox-row"}).get_text().strip()
                        except:
                            publisher = None
                        gamegenre = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_sectionContainer u-flexbox u-flexbox-row u-flexbox-alignBaseline"}).find("span", {"class": "c-globalButton_label"}).get_text().strip()
                        developer = developers if developers else "N/A"
                        publisher = publisher if publisher else "N/A"
                        gamegenre = gamegenre if gamegenre else "N/A"
                    print(f"Adding ---> {game_name}, {game_date}, {rating[0]}, {rating[1]}, {g_platform_concatenated}, {gamegenre}, {publisher}, {developer}")
                    self.data["gamename"].append(game_name)
                    self.data["releasedate"].append(game_date)
                    self.data["metarating"].append(rating[0])
                    self.data["userrating"].append(rating[1])
                    self.data["platform"].append(g_platform_concatenated)
                    self.data["genre"].append(gamegenre)
                    self.data["publisher"].append(publisher)
                    self.data["developer"].append(developer)

            self.browser.get(url)
            productBlockInformation = bs(self.browser.page_source, "html.parser").find_all("div", { "class": "c-finderProductCard c-finderProductCard-game"})
            getInformation(productBlockInformation)
            self.saveData()


        def getPageFilters(self):
            # metacritic filter example url ---> https://www.metacritic.com/browse/game/?releaseYearMin=1997&releaseYearMax=2024&platform=xbox-series-x&platform=nintendo-switch&platform=meta-quest&platform=gamecube&genre=beat---%27em---up&genre=board-or-card-game&genre=first---person-shooter&genre=exercise-or-fitness&genre=open---world&genre=fighting&genre=real---time-strategy&genre=third---person-shooter&genre=party-or-minigame&genre=trivia-or-game-show&genre=turn---based-strategy&genre=shooter&page=1
            # https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2017&platform=ps5&platform=xbox-series-x&platform=nintendo-switch&platform=pc&page=1
            # https://www.metacritic.com/browse/game/all/adventure/all-time/metascore/?releaseYearMin=1958&releaseYearMax=2017&platform=ps5&platform=xbox-series-x&platform=nintendo-switch&platform=pc&genre=adventure&page=1
            # https://www.metacritic.com/browse/game/xbox-one/all/all-time/metascore/?releaseYearMin=1958&releaseYearMax=2024&platform=xbox-one&page=1
            # https://www.metacritic.com/browse/game/ps5/all/all-time/metascore/?releaseYearMin=1958&releaseYearMax=2017&platform=ps5&page=1
            # LittleGamingGeek.s.get()
            self.browser.get("https://metacritic.com/browse/game/")
            filterDate = bs(self.browser.page_source, "html5lib").find("input", {"name":"releaseYearMin"})
            self.filterDate = (filterDate["min"], filterDate["max"])
            all_filters = bs(self.browser.page_source, "html5lib").find_all("div", {"class":"c-filterInput u-grid"})
            self.filters = {}
            def format_text_filter(filters_names, filterTitle, prefix):
                for filter_value_name in filters_names:
                        valueName = filter_value_name.get_text()
                        # Printable text and url encode for filter -> Nintendo Switch / &pataform=nintento-switch
                        replacements = {
                            "'":"%27",
                            "-":"---",
                            " ":"-",
                            "/":"or"
                        }
                        #replace(*[(old, new) for old, new in replacements.items()]) to avoid replace().replace().raplace()
                        formated = valueName
                        for original, replacement in replacements.items():
                            formated = formated.replace(original, replacement).strip().lower()
                        print(f"Trying to add {prefix + formated} to {filterTitle} from {valueName}")
                        self.filters[filterTitle] = {"name":valueName, "added_url":prefix + formated, "selected":False}

            for filter in all_filters:
                filterTitle = bs(str(filter), "html5lib").find("h4").get_text().strip()
                self.filters[filterTitle] = {}
                filter_values = bs(str(filter), "html5lib").find_all("div", {"class":"c-filterInput_content_row u-flexbox"})
                if filterTitle.lower() == "platforms":
                    format_text_filter(filter_values, filterTitle=filterTitle, prefix="&platform=")
                elif filterTitle.lower() == "genre":
                    format_text_filter(filter_values, filterTitle=filterTitle, prefix="&genre=")
                elif filterTitle.lower() == "release type":
                    format_text_filter(filter_values, filterTitle=filterTitle, prefix="&releaseType=")

            self.scrap()
        def saveData(self):
            if self.data:
                DataFrame(self.data).to_csv(join_path(environ["USERPROFILE"], "Desktop/scrap.test.csv"))
            else:
                print("No data in grabbed.")





if __name__ == "__main__":
    gameinfo = LittleGamingGeek()
    gameinfo.metacritic_bot.getPageFilters()
    gameinfo.metacritic_bot.saveData()