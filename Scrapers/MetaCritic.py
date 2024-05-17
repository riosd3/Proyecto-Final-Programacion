from fake_useragent import UserAgent
from time import sleep
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
from tkinter.filedialog import asksaveasfilename
import html5lib
from selenium import webdriver
from pandas import DataFrame
from os import environ
from os.path import join as join_path
from FilterCheck import pagesAvailability
from threading import Thread
def debug(t):print(t);input("<press enter>")
class MetaCritic:
    useragent = UserAgent()
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
    def __init__(self):
        if not pagesAvailability["metacritic"]["filtered"]:
            self.main_url = pagesAvailability["metacritic"]["main_url"]
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument(f"--useragent={self.useragent.random}")
            self.browser = webdriver.Chrome(options=options)
            self.inst_status = True
        else:
            self.inst_status = False
        self.getPageFilters()


    def scrap(self, limit_pages = 0, filters={"Platforms":[], "Release Type":[], "Genre":[]}, verify = False, date_range = (1958, 2024)):
        scrap_url = self.main_url + "/browse/game"
        scrap_url = f"{scrap_url}/?releaseYearMin={date_range[0]}&releaseMaxYear={date_range[1]}"
        for info in filters["Platforms"]:
            scrap_url += info["added_url"]
        for info in filters["Release Type"]:
            scrap_url += info["added_url"]
        for info in filters["Genre"]:
            scrap_url += info["added_url"]
        self.browser.get(scrap_url + "&page=1")
        sleep(1)
        try:
            pageLimits = int(bs(self.browser.page_source, "html5lib").find("span", {"class":"c-finderControls_totalText g-color-gray50"}).get_text().strip().split(" ")[0].replace(",", ""))
        except:
            return 0#print("No results found for this filter combination")
        else:
            if verify:
                return pageLimits
            else:
                self.scraper_counter_total = pageLimits
                self.scraper_counter = 0
                page_num = 1
                while self.scraper_counter < limit_pages:
                    page = scrap_url + f"&page={page_num}"
                    self.add_game(page)
                    page_num += 1


    # add_game is used by scrap to append a game to self.data
    def add_game(self, url):
        print("Starting scrap for: ", url)
        def getInformation(blockinfo):
            for productInfo in blockinfo:
                game_name, game_date, rating, g_platform_concatenated, gamegenre, publisher, developer = None, None, None, None, None, None, None
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
                        publisher = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_Distributor u-flexbox u-flexbox-row"}).find_all("span")[1].get_text().strip()
                    except:
                        publisher = None
                    gamegenre = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_sectionContainer u-flexbox u-flexbox-row u-flexbox-alignBaseline"}).find("span", {"class": "c-globalButton_label"}).get_text().strip()
                    developer = developers if developers else "N/A"
                    publisher = publisher if publisher else "N/A"
                    gamegenre = gamegenre if gamegenre else "N/A"
                self.info_message = f"Adding ---> {game_name}, {game_date}, {rating[0]}, {rating[1]}, {g_platform_concatenated}, {gamegenre}, {publisher}, {developer}\n{self.scraper_counter + 1} of {self.scraper_counter_total}\n"
                print(self.info_message)
                self.data["gamename"].append(game_name)
                self.data["releasedate"].append(game_date)
                self.data["metarating"].append(rating[0])
                self.data["userrating"].append(rating[1])
                self.data["platform"].append(g_platform_concatenated)
                self.data["genre"].append(gamegenre)
                self.data["publisher"].append(publisher)
                self.data["developer"].append(developer)
                self.scraper_counter += 1

        self.browser.get(url)
        with ThreadPoolExecutor(max_workers=100) as executor:
            productBlockInformation = bs(self.browser.page_source, "html.parser").find_all("div", {"class": "c-finderProductCard c-finderProductCard-game"})
            executor.submit(getInformation, productBlockInformation)
        #productBlockInformation = bs(self.browser.page_source, "html.parser").find_all("div", { "class": "c-finderProductCard c-finderProductCard-game"})
        #getInformation(productBlockInformation)


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
                    #print(f"Trying to add {prefix + formated} to {filterTitle} from {valueName}")
                    self.filters[filterTitle.strip()].append({"name":valueName.strip(), "added_url":prefix + formated, "selected":False})

        for filter in all_filters:
            filterTitle = bs(str(filter), "html5lib").find("h4").get_text().strip()
            self.filters[filterTitle] = []
            filter_values = bs(str(filter), "html5lib").find_all("div", {"class":"c-filterInput_content_row u-flexbox"})
            if filterTitle.lower() == "platforms":
                format_text_filter(filter_values, filterTitle=filterTitle, prefix="&platform=")
            elif filterTitle.lower() == "genre":
                format_text_filter(filter_values, filterTitle=filterTitle, prefix="&genre=")
            elif filterTitle.lower() == "release type":
                format_text_filter(filter_values, filterTitle=filterTitle, prefix="&releaseType=")
    def getFilters(self):
        return self.filters
    def getYearFilter(self):
        return self.filterDate


    def save_data(self):
        if self.data:
            file_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if file_path:
                DataFrame(self.data).to_csv(file_path, index=False)
                print("Data saved successfully.")
        else:
            print("No data grabbed.")

if __name__ == "__main__":
    meta = MetaCritic()
    print(meta.getFilters())
    meta.scrap()
