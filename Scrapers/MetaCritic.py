from fake_useragent import UserAgent
from time import sleep
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from tkinter.filedialog import asksaveasfilename
import html5lib
from selenium import webdriver
from pandas import DataFrame
from statistics import mode
from os import environ
from os.path import join as join_path
from FilterCheck import pagesAvailability
from threading import Thread
from SteamCharts import SteamCharts
from PriceGrabber import PriceGrabber
price_scraper = PriceGrabber()
steam_scraper = SteamCharts()
from requests import get
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
        "genre": [],
        "ESRB": [],
        "price": []
    }
    auto_s = 0
    futures_list = []
    part = 0
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


    def scrap(self, limit_pages = 0, filters={"Platforms":[], "Release Type":[], "Genre":[]}, verify = False, date_range = (1958, 2024), price_scraper_obj = 1, stats_scraper_obj = 0, hilos = 1):
        self.price_scraper_obj = price_scraper_obj;self.stats_scraper_obj = stats_scraper_obj;self.hilos = hilos
        self.executor = ThreadPoolExecutor(max_workers=self.hilos)
        scrap_url = self.main_url + "/browse/game"
        scrap_url = f"{scrap_url}/?releaseYearMin={date_range[0]}&releaseMaxYear={date_range[1]}"
        for info in filters["Platforms"]:
            scrap_url += info["added_url"]
        for info in filters["Release Type"]:
            scrap_url += info["added_url"]
        for info in filters["Genre"]:
            scrap_url += info["added_url"]
        self.browser.get(scrap_url + "&page=1")
        #rsp = get(scrap_url + "&page=1")
        try:
            pageLimits = int(bs(self.browser.page_source, "html5lib").find("span", {"class":"c-finderControls_totalText g-color-gray50"}).get_text().strip().split(" ")[0].replace(",", ""))
        except Exception as e:
            return 0#print("No results found for this filter combination")
        else:
            if verify:
                return pageLimits
            else:
                self.scraper_counter_total = pageLimits
                self.scraper_counter = 0
                page_num = 1
                print("Results ", pageLimits)
                while self.scraper_counter < pageLimits:
                    page = scrap_url + f"&page={page_num}"
                    self.add_game(page)
                    page_num += 1
                print("Ending results...")


    # add_game is used by scrap to append a game to self.data
    def add_game(self, url):
        print("Starting scrap for: ", url)
        def getInformation(blockinfo):
            def procutinfo(productInfo):
                game_name, game_date, rating, g_platform_concatenated, gamegenre, publisher, developer = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
                game_name_span = productInfo.find("div", {"class": "c-finderProductCard_title"}).find_all("span")[1]
                game_name = game_name_span.get_text(strip=True) if game_name_span else "N/A"
                # debug(game_name)
                game_date_span = productInfo.find("div", {"class": "c-finderProductCard_meta"}).find_all("span")[0]
                game_date = game_date_span.get_text(strip=True) if game_name_span else "N/A"
                game_rating_span = \
                productInfo.find("span", {"class": "c-finderProductCard_metaItem c-finderProductCard_score"}).find_all(
                    "span")[0]
                game_rating = game_rating_span.get_text(strip=True) if game_name_span else "N/A"
                gameDetails = productInfo.find("a", {"class": "c-finderProductCard_container g-color-gray80 u-grid"})["href"]
                rating = []
                if gameDetails:
                    rspt = get(self.main_url + gameDetails, headers={"User-Agent":self.useragent.random})
                    ratings = bs(rspt.content.decode(), "html5lib").find_all("div", {"class": "c-productScoreInfo_scoreContent u-flexbox u-flexbox-alignCenter u-flexbox-justifyFlexEnd g-width-100 u-flexbox-nowrap"})
                    for i in ratings:
                        r = i.find("span", {"data-v-4cdca868": True}).get_text()
                        rating.append(r) if r else rating.append("N/A")
                    # get plublisher, developer, platform release date, original and gender
                    rspt = get(self.main_url + gameDetails + "details", headers={"User-Agent":self.useragent.random})
                    current_game_info_html_bs_filtrable = bs(rspt.content.decode(), "html5lib")
                    g_platform = current_game_info_html_bs_filtrable.find("div", {"class": "c-gameDetails_sectionContainer u-flexbox u-flexbox-column"}).find_all("li")
                    g_platform_concatenated = []
                    for p in g_platform:
                        g_platform_concatenated.append(p.get_text().strip())
                    g_platform_concatenated = ",".join(g_platform_concatenated)
                    developer_li = current_game_info_html_bs_filtrable.find("div", {
                        "class": "c-gameDetails_Developer u-flexbox u-flexbox-row"}).find_all("li")
                    developers = []
                    for li in developer_li:
                        developer = li.get_text().strip()
                        if developer:
                            developers.append(developer)
                    developers = ",".join(developers)
                    try:
                        publisher = current_game_info_html_bs_filtrable.find("div", {
                            "class": "c-gameDetails_Distributor u-flexbox u-flexbox-row"}).find_all("span")[
                            1].get_text().strip()
                    except Exception as e:
                        print(e, "publisher")
                        publisher = "N/A"
                    gamegenre = current_game_info_html_bs_filtrable.find("div", {
                        "class": "c-gameDetails_sectionContainer u-flexbox u-flexbox-row u-flexbox-alignBaseline"}).find(
                        "span", {"class": "c-globalButton_label"}).get_text().strip()
                    developer = developers if developers else "N/A"
                    publisher = publisher if publisher else "N/A"
                    gamegenre = gamegenre if gamegenre else "N/A"
                gain, p_gain, peak_players = "N/A", "N/A", "N/A"
                if self.stats_scraper_obj and ("pc" in gamegenre.lower()):
                    try:
                        stats_result = steam_scraper.scrap(game_name)
                    except Exception as e:
                        self.data["gain"].append(gain)
                        self.data["percent_gain"].append(p_gain)
                        self.data["peak_players"].append(peak_players)
                    else:
                        gain, p_gain, peak_players = stats_result[3], stats_result[4], stats_result[1]
                        self.data["gain"].append(gain)
                        self.data["percent_gain"].append(p_gain)
                        self.data["peak_players"].append(peak_players)
                price = 0
                if self.price_scraper_obj:
                    try:
                        price = price_scraper.entrySearch(game_name, limit=5, validate_product=g_platform_concatenated.split(","))
                    except Exception as e:
                        print(e, "founding price error ")
                    # try get the ESRB
                    search = game_name.replace(" ", "%20")
                    rspt = get(f"https://www.esrb.org/search/?searchKeyword={search}&platform=All", headers={"User-Agent":self.useragent.random})
                    # Savage because of time
                    clasification = "N/A"
                    try:
                        clasification = bs(str(bs(rspt.content.decode(), "html.parser").find_all("div", {"class": "game"})[0]),"html.parser").find("img").get("alt")
                    except Exception as e:
                        print(e, "clasification values")
                    else:
                        print(clasification)
                    self.data["ESRB"].append(clasification)
                self.info_message = f"Adding ---> {game_name}, {game_date}, {rating[0]}, {rating[1]}, {g_platform_concatenated}, {gamegenre}, {publisher}, {developer}, {price}, {gain}, {p_gain}, {peak_players}, {clasification}\n{self.scraper_counter + 1} of {self.scraper_counter_total}\n"
                print(self.info_message)
                self.data["gamename"].append(game_name)
                self.data["releasedate"].append(game_date)
                self.data["metarating"].append(rating[0])
                self.data["userrating"].append(rating[1])
                self.data["platform"].append(g_platform_concatenated)
                self.data["genre"].append(gamegenre)
                self.data["publisher"].append(publisher)
                self.data["developer"].append(developer)
                self.data["price"].append(price)
                self.scraper_counter += 1
                self.part += 1

                print("Ending product... MetaCritic")

            # Dictionary to hold future objects
            for productInfo in productBlockInformation:
                if len(self.futures_list) == 50:
                    self.part = 0
                    self.auto_s += 1
                    print("Waiting all process to end...", len(self.futures_list), len(list(self.data.values())[0]))
                    done, no_done = wait(self.futures_list)
                    print("All threads end...")
                    self.futures_list = []
                    print("Copying and saving", self.part, len(self.data))
                    self.auto_save_data(self.data.copy())
                    for k in self.data.keys():
                        self.data[k] = []
                self.futures_list.append(self.executor.submit(procutinfo, productInfo))

            #self.futures_list += [self.executor.submit(procutinfo, productInfo);print("Threading") for productInfo in productBlockInformation]
            #self.futures_list.append(futures)

        self.browser.get(url)
        productBlockInformation = bs(self.browser.page_source, "html.parser").find_all("div", {"class": "c-finderProductCard c-finderProductCard-game"})
        getInformation(productBlockInformation)
        #executor.submit(getInformation, productBlockInformation)
    def validate_df(self):
        ttest = []
        def all_equal(lst):
            return all(x == lst[0] for x in lst)

        for t in self.data.values():
            ttest.append(len(t))
        print(ttest)
        """
        if not all_equal(ttest):
            exit(1)"""
    def auto_save_data(self, data):
        print("AUTO SAVING")
        self.validate_df()
        
        try:
            # Step 1: Count the lengths of each list in the data dictionary
            lengths = {k: len(v) for k, v in data.items()}
            print("Column lengths before adjustment:", lengths)
            
            # Step 2: Find the mode (most common length)
            mode_length = mode(lengths.values())
            print("Mode length:", mode_length)
            
            # Step 3: Remove the last element from columns that do not match the mode length
            for k in data.keys():
                while len(data[k]) > mode_length:
                    data[k].pop()
                    
            # Verify lengths after adjustment
            lengths_after = {k: len(v) for k, v in data.items()}
            print("Column lengths after adjustment:", lengths_after)
            
            # Step 4: Save the data to a CSV file
            DataFrame(data).to_csv(join_path(environ["USERPROFILE"], f"Desktop/scraps/GamingG.{self.auto_s}.csv"))
        except Exception as e:
            print(e, "ERROR SAVING DATA...")
        else:
            print("DATA FRAME SAVED SUCCESSFULLY")

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
                        "x/s":"x"
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
        ttest = []
        def all_equal(lst):
            return all(x == lst[0] for x in lst)
        for t in self.data.values():
            ttest.append(len(t))
        print(ttest)
        if not all_equal(ttest):
            exit(1)
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
