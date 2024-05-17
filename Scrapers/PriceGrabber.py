from sys import exit as sys_exit
from fake_useragent import UserAgent
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from pandas import DataFrame
from selenium.webdriver.common.by import By
from requests import get, Session
from os import environ
from os.path import join as join_path
from FilterCheck import pagesAvailability

class PriceGrabber:
    ranWebAgent = UserAgent()
    def __init__(self):
        if not pagesAvailability["pricegrabber"]["filtered"]:
            self.main_url = "https://www.pricegrabber.com"
            options = webdriver.ChromeOptions()
            options.add_argument(f"--useragent={PriceGrabber.ranWebAgent.random}")
            options.add_argument("--headless")
            self.selenium_browser = webdriver.Chrome(options=options)
            self.requests_browser = Session()
            self.requests_browser.headers.update({"User-Agent":PriceGrabber.ranWebAgent.random})
            self.inst_status = True
        else:
            self.inst_status = False

    def getFilters(self):
        main_url = self.main_url + "/videogames1/browse/"
        r = self.requests_browser.get(main_url)
        console_tags = BeautifulSoup(r.content, "html.parser").find_all("div", {"class":"col clearfix"})[1]
        lu_tags = console_tags.find_all("ul")[0]
        filters_info = []
        for a_tags in lu_tags.find_all("a"):
            try:
                console_name = a_tags.get_text().strip()
                href = a_tags.get("href")
            except:
                print("Can not get console or href")
            else:
                filters_info.append({"console_name":console_name, "href":href})
        return filters_info
    def entrySearch(self, search, filters=None, limit=None):
        if self.selenium_browser:
            self.selenium_browser.get(self.main_url)
            sleep(2)
            searchBar = self.selenium_browser.find_element(By.ID, "shopForInput")
            searchButton = self.selenium_browser.find_element(By.ID, "search_submit")
            searchBar.send_keys(search)
            searchButton.click()
            a = True
            counter = 1
            while a:
                result = self.selenium_browser.page_source
                try:
                    page_filtrable = BeautifulSoup(result, "html.parser")
                    result = page_filtrable.find("div", {"class":"resultsListProductCount"}).get_text().strip()
                except:
                    print("There is not result for this search...", search)
                else:
                    try:
                        max_result = int(result.split()[0])
                        items = page_filtrable.find_all("div", {"class":"product product_item"})
                        items_len = len(items)
                    except:
                        print("Could not get the products cards for the current page")
                        a = False
                    else:
                        if limit > max_result:
                            limit = max_result
                        for i in items:
                            if counter <= limit:
                                try:
                                    title = i.find("a", {"class":"resultsListTitle colorLink"}).get("data-product-title")
                                except:
                                    title = "N/A"
                                try:
                                    price = i.find("p", {"class":"ctaPrice"}).find("a", {"class":"productPrice colorLink"}).find_all("span")[1].get_text().strip()
                                except:
                                    price = "N/A"
                                print(counter, title, price)
                                counter += 1
                        if counter < limit:
                            try:
                                next_page_link = BeautifulSoup(self.selenium_browser.page_source, "html.parser").find("a", {"class":"next colorLink"}).get("href")
                                print(next_page_link)
                            except:
                                a = False
                            else:
                                self.selenium_browser.get(self.main_url + next_page_link)
                        else:
                            a = False

if __name__ == "__main__":
    p = PriceGrabber()
    if p.inst_status:
        p.entrySearch(search="The Legend of Zelda: The Wind Waker Nintendo", limit=5)
